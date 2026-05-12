from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from schema.usuario_schema import UsuarioCreate, UsuarioRead, UsuarioUpdate
from services import usuario_service
from utils.dependencies import get_current_user, get_db


router = APIRouter(
    prefix="/usuarios",
    tags=["usuarios"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
def crear_usuario(payload: UsuarioCreate, db: Session = Depends(get_db)) -> UsuarioRead:
    usuario = usuario_service.create_usuario(db, payload)
    return UsuarioRead.model_validate(usuario)


@router.get("/", response_model=list[UsuarioRead])
def listar_usuarios(db: Session = Depends(get_db)) -> list[UsuarioRead]:
    usuarios = usuario_service.list_usuarios(db)
    return [UsuarioRead.model_validate(usuario) for usuario in usuarios]


@router.get("/{usuario_id}", response_model=UsuarioRead)
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)) -> UsuarioRead:
    usuario = usuario_service.get_usuario_or_404(db, usuario_id)
    return UsuarioRead.model_validate(usuario)


@router.put("/{usuario_id}", response_model=UsuarioRead)
def actualizar_usuario(
    usuario_id: int,
    payload: UsuarioUpdate,
    db: Session = Depends(get_db),
) -> UsuarioRead:
    usuario = usuario_service.update_usuario(db, usuario_id, payload)
    return UsuarioRead.model_validate(usuario)


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)) -> Response:
    usuario_service.delete_usuario(db, usuario_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
