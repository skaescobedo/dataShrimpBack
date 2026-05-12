from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config import settings
from schema.usuario_schema import LoginRequest, Token, UsuarioCreate, UsuarioRead
from services import usuario_service
from utils.dependencies import get_db
from utils.security import create_access_token, verify_password


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
def register(payload: UsuarioCreate, db: Session = Depends(get_db)) -> UsuarioRead:
    usuario = usuario_service.create_usuario(db, payload)
    return UsuarioRead.model_validate(usuario)


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Token:
    usuario = usuario_service.get_usuario_by_correo(db, payload.correo)
    if not usuario or not verify_password(payload.password, usuario.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    access_token = create_access_token(
        data={"sub": str(usuario.id_usuario)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(access_token=access_token)
