from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CicloEstanqueBase(BaseModel):
    id_ciclo: int
    id_estanque: int
    fecha_siembra: date
    densidad_inicial_m2: Decimal
    peso_inicial_promedio_g: Decimal | None = None
    estado: str = "activo"


class CicloEstanqueCreate(CicloEstanqueBase):
    pass


class CicloEstanqueUpdate(BaseModel):
    fecha_siembra: date | None = None
    densidad_inicial_m2: Decimal | None = None
    peso_inicial_promedio_g: Decimal | None = None
    estado: str | None = None


class CicloEstanqueFinalizar(BaseModel):
    estado: str = "finalizado"


class CicloEstanqueRead(CicloEstanqueBase):
    id_ciclo_estanque: int

    model_config = ConfigDict(from_attributes=True)
