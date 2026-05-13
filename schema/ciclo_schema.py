from datetime import date, datetime
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, field_serializer


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
    
    @field_serializer('creado_en')
    def serialize_creado_en(self, value: datetime) -> str:
        if value:
            tz_mazatlan = ZoneInfo("America/Mazatlan")
            local_time = value.replace(tzinfo=ZoneInfo("UTC")).astimezone(tz_mazatlan)
            return local_time.strftime('%Y-%m-%d %H:%M')
        return None
