from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.usuario import Usuario
from schema.usuario_schema import UsuarioCreate, UsuarioUpdate
from utils.security import hash_password


def get_usuario_by_correo(db: Session, correo: str) -> Usuario | None:
    return db.scalar(select(Usuario).where(Usuario.correo == correo))


def create_usuario(db: Session, payload: UsuarioCreate) -> Usuario:
    if get_usuario_by_correo(db, payload.correo):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El correo ya existe")

    usuario = Usuario(
        nombre=payload.nombre,
        correo=payload.correo,
        password=hash_password(payload.password),
        rol=payload.rol,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def list_usuarios(db: Session) -> list[Usuario]:
    return list(db.scalars(select(Usuario).order_by(Usuario.id_usuario)).all())


def get_usuario_or_404(db: Session, usuario_id: int) -> Usuario:
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return usuario


def update_usuario(db: Session, usuario_id: int, payload: UsuarioUpdate) -> Usuario:
    usuario = get_usuario_or_404(db, usuario_id)
    data = payload.model_dump(exclude_unset=True)

    if "correo" in data and data["correo"] != usuario.correo:
        if get_usuario_by_correo(db, data["correo"]):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El correo ya existe")

    if "password" in data:
        data["password"] = hash_password(data["password"])

    for field, value in data.items():
        setattr(usuario, field, value)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fue posible actualizar") from exc

    db.refresh(usuario)
    return usuario


def delete_usuario(db: Session, usuario_id: int) -> None:
    usuario = get_usuario_or_404(db, usuario_id)
    db.delete(usuario)
    db.commit()
