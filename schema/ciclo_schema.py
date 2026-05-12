from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class CicloBase(BaseModel):
    nombre: str
    fecha_inicio: date
    fecha_fin: date | None = None
    estado: str = "activo"


class CicloCreate(CicloBase):
    pass


class CicloUpdate(BaseModel):
    nombre: str | None = None
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    estado: str | None = None


class CicloFinalizar(BaseModel):
    fecha_fin: date | None = None


class CicloRead(CicloBase):
    id_ciclo: int
    creado_en: datetime

    model_config = ConfigDict(from_attributes=True)
