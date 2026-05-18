from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.ciclo import Ciclo
from models.ciclo_estanque import CicloEstanque
from models.estanque import Estanque
from schema.ciclo_estanque_schema import CicloEstanqueCreate, CicloEstanqueUpdate


def create_ciclo_estanque(db: Session, payload: CicloEstanqueCreate) -> CicloEstanque:
    if not db.get(Ciclo, payload.id_ciclo):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ciclo no encontrado")
    if not db.get(Estanque, payload.id_estanque):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estanque no encontrado")

    if payload.densidad_inicial_m2 < Decimal("1") or payload.densidad_inicial_m2 > Decimal("500"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La densidad inicial debe estar entre 1 y 500 org/m²")

    if payload.peso_inicial_promedio_g is not None and (payload.peso_inicial_promedio_g < Decimal("0.01") or payload.peso_inicial_promedio_g > Decimal("10")):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El peso inicial promedio debe estar entre 0.01 y 10 g")

    ciclo_estanque = CicloEstanque(**payload.model_dump())
    db.add(ciclo_estanque)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La asociación ciclo-estanque ya existe",
        ) from exc

    db.refresh(ciclo_estanque)
    return ciclo_estanque


def list_by_ciclo(db: Session, ciclo_id: int) -> list[CicloEstanque]:
    return list(
        db.scalars(
            select(CicloEstanque)
            .where(CicloEstanque.id_ciclo == ciclo_id)
            .order_by(CicloEstanque.id_ciclo_estanque)
        ).all()
    )


def list_by_estanque(db: Session, estanque_id: int) -> list[CicloEstanque]:
    return list(
        db.scalars(
            select(CicloEstanque)
            .where(CicloEstanque.id_estanque == estanque_id)
            .order_by(CicloEstanque.id_ciclo_estanque)
        ).all()
    )


def get_ciclo_estanque_or_404(db: Session, ciclo_estanque_id: int) -> CicloEstanque:
    ciclo_estanque = db.get(CicloEstanque, ciclo_estanque_id)
    if not ciclo_estanque:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asociación no encontrada")
    return ciclo_estanque


def update_ciclo_estanque(
    db: Session, ciclo_estanque_id: int, payload: CicloEstanqueUpdate
) -> CicloEstanque:
    ciclo_estanque = get_ciclo_estanque_or_404(db, ciclo_estanque_id)
    data = payload.model_dump(exclude_unset=True)

    if "densidad_inicial_m2" in data and (data["densidad_inicial_m2"] < Decimal("1") or data["densidad_inicial_m2"] > Decimal("500")):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La densidad inicial debe estar entre 1 y 500 org/m²")

    if "peso_inicial_promedio_g" in data and data["peso_inicial_promedio_g"] is not None and (data["peso_inicial_promedio_g"] < Decimal("0.01") or data["peso_inicial_promedio_g"] > Decimal("10")):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El peso inicial promedio debe estar entre 0.01 y 10 g")

    for field, value in data.items():
        setattr(ciclo_estanque, field, value)
    db.commit()
    db.refresh(ciclo_estanque)
    return ciclo_estanque


def finalizar_ciclo_estanque(db: Session, ciclo_estanque_id: int) -> CicloEstanque:
    ciclo_estanque = get_ciclo_estanque_or_404(db, ciclo_estanque_id)
    ciclo_estanque.estado = "finalizado"
    db.commit()
    db.refresh(ciclo_estanque)
    return ciclo_estanque


def delete_ciclo_estanque(db: Session, ciclo_estanque_id: int) -> None:
    ciclo_estanque = get_ciclo_estanque_or_404(db, ciclo_estanque_id)
    db.delete(ciclo_estanque)
    db.commit()
