from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class EstanqueBase(BaseModel):
    nombre: str
    ubicacion: str | None = None
    superficie_m2: Decimal
    estado: str = "activo"


class EstanqueCreate(EstanqueBase):
    pass


class EstanqueUpdate(BaseModel):
    nombre: str | None = None
    ubicacion: str | None = None
    superficie_m2: Decimal | None = None
    estado: str | None = None


class EstanqueRead(EstanqueBase):
    id_estanque: int
    creado_en: datetime

    model_config = ConfigDict(from_attributes=True)
