from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any

from utils.dependencies import get_db, get_current_user
from models.biometria import Biometria
from models.ciclo_estanque import CicloEstanque
from models.ciclo import Ciclo
from models.estanque import Estanque

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/general-growth")
def get_general_growth(
    ciclo_estanque_id: int = None,
    ciclo_id: int = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> List[Dict[str, Any]]:

    # Caso 1: por estanque específico — promedio de registros del mismo día
    if ciclo_estanque_id is not None:
        data = (
            db.query(
                Biometria.fecha,
                func.avg(Biometria.peso_promedio_g).label('avg_peso')
            )
            .filter(Biometria.id_ciclo_estanque == ciclo_estanque_id)
            .group_by(Biometria.fecha)
            .order_by(Biometria.fecha)
            .all()
        )
        return [{"fecha": d.fecha.isoformat(), "peso_promedio": float(d.avg_peso)} for d in data]

    # Caso 2: por ciclo completo
    if ciclo_id is not None:

        # Paso 1: fechas distintas con biometría en el ciclo
        fechas_query = (
            db.query(Biometria.fecha)
            .join(CicloEstanque, Biometria.id_ciclo_estanque == CicloEstanque.id_ciclo_estanque)
            .filter(CicloEstanque.id_ciclo == ciclo_id)
            .distinct()
            .order_by(Biometria.fecha)
            .all()
        )
        fechas = [f.fecha for f in fechas_query]

        # Paso 2: estanques que pertenecen al ciclo
        ciclo_estanques_ids = (
            db.query(CicloEstanque.id_ciclo_estanque)
            .filter(CicloEstanque.id_ciclo == ciclo_id)
            .all()
        )
        ce_ids = [ce.id_ciclo_estanque for ce in ciclo_estanques_ids]

        if not fechas or not ce_ids:
            return []

        # Paso 3: para cada fecha, para cada estanque,
        # promedio del día si hay registros, o último disponible antes de esa fecha
        result = []
        for fecha in fechas:
            pesos = []
            for ce_id in ce_ids:

                # Registros del mismo día → promedio
                mismo_dia = (
                    db.query(func.avg(Biometria.peso_promedio_g))
                    .filter(
                        Biometria.id_ciclo_estanque == ce_id,
                        Biometria.fecha == fecha
                    )
                    .scalar()
                )

                if mismo_dia is not None:
                    pesos.append(float(mismo_dia))
                else:
                    # Último registro disponible antes de esta fecha
                    ultimo = (
                        db.query(Biometria.peso_promedio_g)
                        .filter(
                            Biometria.id_ciclo_estanque == ce_id,
                            Biometria.fecha < fecha
                        )
                        .order_by(Biometria.fecha.desc(), Biometria.id_biometria.desc())
                        .first()
                    )
                    if ultimo is not None:
                        pesos.append(float(ultimo.peso_promedio_g))
                    # Si no hay ningún registro anterior, ese estanque no contribuye

            if pesos:
                result.append({
                    "fecha": fecha.isoformat(),
                    "peso_promedio": sum(pesos) / len(pesos)
                })

        return result

    return []

@router.get("/ranking-estanques/{ciclo_id}")
def get_ranking_estanques(
    ciclo_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> List[Dict[str, Any]]:

    # Subquery: última biometría por estanque (según fecha)
    latest_subquery = db.query(
        Biometria.id_ciclo_estanque,
        func.max(Biometria.fecha).label("max_fecha")
    ).group_by(
        Biometria.id_ciclo_estanque
    ).subquery()

    # Query principal: ranking por peso promedio más reciente
    query = (
        db.query(
            Estanque.nombre,
            Biometria.peso_promedio_g
        )
        .join(
            CicloEstanque,
            Estanque.id_estanque == CicloEstanque.id_estanque
        )
        .join(
            Biometria,
            CicloEstanque.id_ciclo_estanque == Biometria.id_ciclo_estanque
        )
        .join(
            latest_subquery,
            (Biometria.id_ciclo_estanque == latest_subquery.c.id_ciclo_estanque) &
            (Biometria.fecha == latest_subquery.c.max_fecha)
        )
        .filter(
            CicloEstanque.id_ciclo == ciclo_id
        )
    )

    data = query.order_by(
        Biometria.peso_promedio_g.desc()
    ).all()

    return [
        {
            "estanque": d.nombre,
            "peso_promedio": float(d.peso_promedio_g)
        }
        for d in data
    ]
@router.get("/growth-relations/{ciclo_estanque_id}")
def get_growth_relations(ciclo_estanque_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)) -> List[Dict[str, Any]]:
    # Relación crecimiento vs temperatura vs oxígeno vs salinidad
    data = db.query(Biometria).filter(Biometria.id_ciclo_estanque == ciclo_estanque_id).order_by(Biometria.fecha).all()
    return [{
        "fecha": d.fecha.isoformat(),
        "peso": float(d.peso_promedio_g),
        "temp": float(d.agua_temperatura),
        "oxigeno": float(d.agua_oxigeno),
        "salinidad": float(d.agua_salinidad)
    } for d in data]

@router.get("/compare-growth/{ciclo_id}")
def compare_growth(
    ciclo_id: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    # Comparativa de crecimiento entre todos los estanques de un ciclo
    data = db.query(Biometria.fecha, Estanque.nombre, func.avg(Biometria.peso_promedio_g).label('peso')).join(CicloEstanque, Biometria.id_ciclo_estanque == CicloEstanque.id_ciclo_estanque).join(Estanque, CicloEstanque.id_estanque == Estanque.id_estanque).filter(CicloEstanque.id_ciclo == ciclo_id).group_by(Biometria.fecha, Estanque.nombre).all()
    
    merged_data: Dict[str, Any] = {}
    for d in data:
        fecha_iso = d.fecha.isoformat()
        if fecha_iso not in merged_data:
            merged_data[fecha_iso] = {"fecha": fecha_iso}
        merged_data[fecha_iso][d.nombre] = float(d.peso)
            
    # Ordenar por fecha cronológicamente
    return [merged_data[k] for k in sorted(merged_data.keys())]
