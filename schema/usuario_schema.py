from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UsuarioBase(BaseModel):
    nombre: str
    correo: EmailStr
    rol: str = "usuario"


class UsuarioCreate(UsuarioBase):
    password: str


class UsuarioUpdate(BaseModel):
    nombre: str | None = None
    correo: EmailStr | None = None
    password: str | None = None
    rol: str | None = None


class UsuarioRead(UsuarioBase):
    id_usuario: int
    creado_en: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    correo: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
