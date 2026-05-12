from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.ciclo import Ciclo
from schema.ciclo_schema import CicloCreate, CicloUpdate


def create_ciclo(db: Session, payload: CicloCreate) -> Ciclo:
    ciclo = Ciclo(**payload.model_dump())
    db.add(ciclo)
    db.commit()
    db.refresh(ciclo)
    return ciclo


def list_ciclos(db: Session) -> list[Ciclo]:
    return list(db.scalars(select(Ciclo).order_by(Ciclo.id_ciclo)).all())


def get_ciclo_or_404(db: Session, ciclo_id: int) -> Ciclo:
    ciclo = db.get(Ciclo, ciclo_id)
    if not ciclo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ciclo no encontrado")
    return ciclo


def update_ciclo(db: Session, ciclo_id: int, payload: CicloUpdate) -> Ciclo:
    ciclo = get_ciclo_or_404(db, ciclo_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(ciclo, field, value)
    db.commit()
    db.refresh(ciclo)
    return ciclo


def finalizar_ciclo(db: Session, ciclo_id: int, fecha_fin: date | None) -> Ciclo:
    ciclo = get_ciclo_or_404(db, ciclo_id)
    ciclo.fecha_fin = fecha_fin or date.today()
    ciclo.estado = "finalizado"
    db.commit()
    db.refresh(ciclo)
    return ciclo


def delete_ciclo(db: Session, ciclo_id: int) -> None:
    ciclo = get_ciclo_or_404(db, ciclo_id)
    db.delete(ciclo)
    db.commit()
