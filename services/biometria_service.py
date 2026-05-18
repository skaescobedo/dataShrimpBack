from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import UploadFile, File
import pandas as pd
import io
from fastapi import HTTPException, status
from sklearn.linear_model import LinearRegression
import numpy as np

from models.biometria import Biometria
from models.ciclo_estanque import CicloEstanque
from models.ciclo import Ciclo
from models.estanque import Estanque
from schema.biometria_schema import BiometriaCreate, BiometriaUpdate

COLUMN_ALIASES = {
    "fecha": ["fecha", "date", "dia", "día"],
    "ciclo": ["ciclo", "ciclo estanque", "ciclo", "ciclo estanque"],
    "estanque": ["estanque", "id estanque", "estanque id", "id_estanque"],
    "numero_muestra": ["n° muestra", "no muestra", "num muestra", "numero muestra"],
    "peso_total_muestra_g": ["peso total (g)", "peso total", "peso_total", "peso total (gr)"],
    "agua_temperatura": ["temperatura agua(°c)", "temperatura agua", "temp agua", "temperatura agua (C°)"],
    "agua_salinidad": ["salinidad (ppt)", "salinidad", "sal", "agua salinidad"],
    "agua_oxigeno": ["oxígeno disuelto (mg/l)", "oxigeno disuelto", "o2", "od"],
}


def _calcular_peso_promedio(peso_total: Decimal, numero_muestra: int) -> Decimal:
    if numero_muestra <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="numero_muestra debe ser mayor a 0")
    return (peso_total / Decimal(numero_muestra)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def create_biometria(db: Session, payload: BiometriaCreate, usuario_id: int) -> Biometria:
    if not db.get(CicloEstanque, payload.id_ciclo_estanque):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ciclo estanque no encontrado")

    peso_promedio = _calcular_peso_promedio(payload.peso_total_muestra_g, payload.numero_muestra)
    biometria = Biometria(
        **payload.model_dump(),
        peso_promedio_g=peso_promedio,
        registrado_por=usuario_id,
    )
    db.add(biometria)
    db.commit()
    db.refresh(biometria)
    return biometria


def list_biometrias(db: Session) -> list[Biometria]:
    return list(db.scalars(select(Biometria).order_by(Biometria.id_biometria)).all())


def list_biometrias_by_ciclo_estanque(db: Session, ciclo_estanque_id: int) -> list[Biometria]:
    return list(
        db.scalars(
            select(Biometria)
            .where(Biometria.id_ciclo_estanque == ciclo_estanque_id)
            .order_by(Biometria.id_biometria)
        ).all()
    )


def get_biometria_or_404(db: Session, biometria_id: int) -> Biometria:
    biometria = db.get(Biometria, biometria_id)
    if not biometria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Biometría no encontrada")
    return biometria


def update_biometria(db: Session, biometria_id: int, payload: BiometriaUpdate) -> Biometria:
    biometria = get_biometria_or_404(db, biometria_id)
    data = payload.model_dump(exclude_unset=True)

    if "id_ciclo_estanque" in data and not db.get(CicloEstanque, data["id_ciclo_estanque"]):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ciclo estanque no encontrado")

    numero_muestra = data.get("numero_muestra", biometria.numero_muestra)
    peso_total_muestra_g = data.get("peso_total_muestra_g", biometria.peso_total_muestra_g)
    data["peso_promedio_g"] = _calcular_peso_promedio(peso_total_muestra_g, numero_muestra)

    for field, value in data.items():
        setattr(biometria, field, value)

    db.commit()
    db.refresh(biometria)
    return biometria


def delete_biometria(db: Session, biometria_id: int) -> None:
    biometria = get_biometria_or_404(db, biometria_id)
    db.delete(biometria)
    db.commit()

def find_column(df: pd.DataFrame, aliases: list[str]) -> str | None:
    for alias in aliases:
        for col in df.columns:
            if alias.lower().strip() == col.lower().strip():
                return col
    return None


def get_ciclo_by_nombre(db: Session, nombre: str) -> Ciclo | None:
    """Busca un ciclo por nombre exacto (case-insensitive)"""
    return db.scalars(
        select(Ciclo).where(Ciclo.nombre.ilike(nombre))
    ).first()


def get_estanque_by_nombre(db: Session, nombre: str) -> Estanque | None:
    """Busca un estanque por nombre exacto (case-insensitive)"""
    return db.scalars(
        select(Estanque).where(Estanque.nombre.ilike(nombre))
    ).first()


def validate_ciclo_estanque_association(db: Session, ciclo_nombre: str, estanque_nombre: str) -> CicloEstanque:
    """
    Valida que ciclo y estanque existan y estén asociados.
    Retorna el CicloEstanque si todo es válido, sino lanza HTTPException.
    """
    ciclo = get_ciclo_by_nombre(db, ciclo_nombre)
    if not ciclo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ciclo '{ciclo_nombre}' no existe"
        )
    
    estanque = get_estanque_by_nombre(db, estanque_nombre)
    if not estanque:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Estanque '{estanque_nombre}' no existe"
        )
    
    ciclo_estanque = db.scalars(
        select(CicloEstanque).where(
            (CicloEstanque.id_ciclo == ciclo.id_ciclo) &
            (CicloEstanque.id_estanque == estanque.id_estanque)
        )
    ).first()
    
    if not ciclo_estanque:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El ciclo '{ciclo_nombre}' y el estanque '{estanque_nombre}' no están asociados"
        )
    
    return ciclo_estanque


async def processBiometriaFromExcel(db: Session, archive: UploadFile=File(...)) -> list[BiometriaCreate]:
    content = await archive.read()
    df = pd.read_excel(io.BytesIO(content))
    col_map = {}
    for field, aliases in COLUMN_ALIASES.items():
        found = find_column(df, aliases)
        if found:
            col_map[field] = found
        else:
            raise HTTPException(
                status_code=400,
                detail=f"No se encontró la columna '{field}'. Nombres aceptados: {aliases}"
            )
    register = []
    for _, row in df.iterrows():
        ciclo_nombre = row[col_map["ciclo"]]
        estanque_nombre = row[col_map["estanque"]]
        
        # Validar que ciclo y estanque existan y estén asociados
        ciclo_estanque = validate_ciclo_estanque_association(db, ciclo_nombre, estanque_nombre)
        
        register.append(BiometriaCreate(
            id_ciclo_estanque=ciclo_estanque.id_ciclo_estanque,
            ciclo=row[col_map["ciclo"]],
            estanque=row[col_map["estanque"]],
            fecha=row[col_map["fecha"]],
            numero_muestra=int(row[col_map["numero_muestra"]]),
            peso_total_muestra_g=float(row[col_map["peso_total_muestra_g"]]),
            agua_temperatura=float(row[col_map["agua_temperatura"]]),
            agua_salinidad=float(row[col_map["agua_salinidad"]]),
            agua_oxigeno=float(row[col_map["agua_oxigeno"]]),
        ))

    return register


def _obtener_datos_entrenamiento(db: Session) -> tuple[np.ndarray, list[dict], dict]:
    # Obtener todos los registros de biometría ordenados
    all_biometrias = list(
        db.scalars(
            select(Biometria)
            .join(CicloEstanque)
            .order_by(CicloEstanque.id_ciclo_estanque, Biometria.fecha)
        ).all()
    )
    
    if len(all_biometrias) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Se necesitan al menos 3 registros históricos para entrenar el modelo"
        )
    
    ciclo_estanque_biometrias = {}
    data_training = []
    
    for biometria in all_biometrias:
        ciclo_est = db.get(CicloEstanque, biometria.id_ciclo_estanque)
        if ciclo_est.id_ciclo_estanque not in ciclo_estanque_biometrias:
            ciclo_estanque_biometrias[ciclo_est.id_ciclo_estanque] = []
        
        ciclo_estanque_biometrias[ciclo_est.id_ciclo_estanque].append(biometria)
    
    for ciclo_est_id, biometrias_grupo in ciclo_estanque_biometrias.items():
        ciclo_est = db.get(CicloEstanque, ciclo_est_id)
        for idx, biometria in enumerate(biometrias_grupo, 1):
            data_training.append({
                'numero_biometria': idx,
                'ciclo_estanque_id': ciclo_est_id,
                'fecha': biometria.fecha,
                'peso_promedio': float(biometria.peso_promedio_g),
                'temperatura': float(biometria.agua_temperatura),
                'salinidad': float(biometria.agua_salinidad),
                'oxigeno': float(biometria.agua_oxigeno)
            })
    
    # Construir X y y para cada output
    X = np.array([[d['numero_biometria'], d['temperatura'], d['salinidad'], d['oxigeno']] 
                   for d in data_training])
    
    y_peso = np.array([d['peso_promedio'] for d in data_training])
    y_temp = np.array([d['temperatura'] for d in data_training])
    y_sal = np.array([d['salinidad'] for d in data_training])
    y_ox = np.array([d['oxigeno'] for d in data_training])
    
    modelos = {
        'peso': LinearRegression().fit(X, y_peso),
        'temperatura': LinearRegression().fit(X, y_temp),
        'salinidad': LinearRegression().fit(X, y_sal),
        'oxigeno': LinearRegression().fit(X, y_ox)
    }
    
    return X, data_training, modelos


def predict_biometria_global(db: Session, ciclo_estanque_id: int, semanas_futuras: int = 4) -> dict:

    # Validar ciclo_estanque existe
    ciclo_estanque = db.get(CicloEstanque, ciclo_estanque_id)
    if not ciclo_estanque:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ciclo estanque no encontrado")
    
    ultima_biometria = db.scalars(
        select(Biometria)
        .where(Biometria.id_ciclo_estanque == ciclo_estanque_id)
        .order_by(Biometria.fecha.desc())
    ).first()
    
    if not ultima_biometria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay biometrías registradas para este ciclo-estanque"
        )
    
    biometrias_ciclo = list(
        db.scalars(
            select(Biometria)
            .where(Biometria.id_ciclo_estanque == ciclo_estanque_id)
            .order_by(Biometria.fecha)
        ).all()
    )
    numero_biometria_actual = len(biometrias_ciclo)
    
    X, data_training, modelos = _obtener_datos_entrenamiento(db)
    
    r2_peso = modelos['peso'].score(X, np.array([d['peso_promedio'] for d in data_training]))
    
    temp_actual = float(ultima_biometria.agua_temperatura)
    sal_actual = float(ultima_biometria.agua_salinidad)
    ox_actual = float(ultima_biometria.agua_oxigeno)
    
    # Hacer predicciones
    predicciones = []
    for i in range(1, semanas_futuras + 1):
        numero_bio_futuro = numero_biometria_actual + i
        fecha_futura = ultima_biometria.fecha + timedelta(days=7 * i)
        
        # Ajustar features: para predicciones futuras, usar valores proyectados de agua
        X_pred = np.array([[numero_bio_futuro, temp_actual, sal_actual, ox_actual]])
        
        peso_pred = float(modelos['peso'].predict(X_pred)[0])
        temp_pred = float(modelos['temperatura'].predict(X_pred)[0])
        sal_pred = float(modelos['salinidad'].predict(X_pred)[0])
        ox_pred = float(modelos['oxigeno'].predict(X_pred)[0])
        
        predicciones.append({
            'numero_biometria': numero_bio_futuro,
            'fecha': fecha_futura,
            'peso_promedio_predicho': max(0, round(peso_pred, 2)),
            'agua_temperatura_predicha': max(0, round(temp_pred, 2)),
            'agua_salinidad_predicha': max(0, round(sal_pred, 2)),
            'agua_oxigeno_predicho': max(0, round(ox_pred, 2)),
            'confianza': round(r2_peso, 4)
        })
    
    return {
        'ciclo_nombre': ciclo_estanque.ciclo.nombre,
        'estanque_nombre': ciclo_estanque.estanque.nombre,
        'numero_biometria_actual': numero_biometria_actual,
        'fecha_siembra': ciclo_estanque.fecha_siembra,
        'predicciones': predicciones,
        'r2_modelo': round(r2_peso, 4),
        'cantidad_datos_entrenamiento': len(data_training)
    }
