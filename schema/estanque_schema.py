from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, field_serializer


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
    
    @field_serializer('creado_en')
    def serialize_creado_en(self, value: datetime) -> str:
        if value:
            tz_mazatlan = ZoneInfo("America/Mazatlan")
            local_time = value.replace(tzinfo=ZoneInfo("UTC")).astimezone(tz_mazatlan)
            return local_time.strftime('%Y-%m-%d %H:%M')
        return None