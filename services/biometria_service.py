from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.biometria import Biometria
from models.ciclo_estanque import CicloEstanque
from schema.biometria_schema import BiometriaCreate, BiometriaUpdate


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
