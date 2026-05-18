from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BiometriaBase(BaseModel):
    id_ciclo_estanque: int
    fecha: date
    numero_muestra: int
    peso_total_muestra_g: Decimal
    agua_temperatura: Decimal
    agua_salinidad: Decimal
    agua_oxigeno: Decimal
    observaciones: str | None = None


class BiometriaCreate(BaseModel):
    id_ciclo_estanque: int
    fecha: date
    numero_muestra: int
    peso_total_muestra_g: Decimal
    agua_temperatura: Decimal
    agua_salinidad: Decimal
    agua_oxigeno: Decimal
    observaciones: str | None = None


class BiometriaUpdate(BaseModel):
    id_ciclo_estanque: int | None = None
    fecha: date | None = None
    numero_muestra: int | None = None
    peso_total_muestra_g: Decimal | None = None
    agua_temperatura: Decimal | None = None
    agua_salinidad: Decimal | None = None
    agua_oxigeno: Decimal | None = None
    observaciones: str | None = None


class BiometriaRead(BiometriaBase):
    id_biometria: int
    peso_promedio_g: Decimal
    registrado_por: int
    creado_en: datetime

    model_config = ConfigDict(from_attributes=True)
