from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.estanque import Estanque
from schema.estanque_schema import EstanqueCreate, EstanqueUpdate


def create_estanque(db: Session, payload: EstanqueCreate) -> Estanque:
    estanque = Estanque(**payload.model_dump())
    db.add(estanque)
    db.commit()
    db.refresh(estanque)
    return estanque


def list_estanques(db: Session) -> list[Estanque]:
    return list(db.scalars(select(Estanque).order_by(Estanque.id_estanque)).all())


def get_estanque_or_404(db: Session, estanque_id: int) -> Estanque:
    estanque = db.get(Estanque, estanque_id)
    if not estanque:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estanque no encontrado")
    return estanque


def update_estanque(db: Session, estanque_id: int, payload: EstanqueUpdate) -> Estanque:
    estanque = get_estanque_or_404(db, estanque_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(estanque, field, value)
    db.commit()
    db.refresh(estanque)
    return estanque


def delete_estanque(db: Session, estanque_id: int) -> None:
    estanque = get_estanque_or_404(db, estanque_id)
    db.delete(estanque)
    db.commit()
