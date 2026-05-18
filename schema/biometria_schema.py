from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BiometriaBase(BaseModel):
    id_ciclo_estanque: int
    fecha: date
    numero_muestra: int = Field(gt=0)
    peso_total_muestra_g: Decimal = Field(gt=0)
    agua_temperatura: Decimal = Field(gt=0)
    agua_salinidad: Decimal = Field(gt=0)
    agua_oxigeno: Decimal = Field(gt=0)
    observaciones: str | None = None


class BiometriaCreate(BiometriaBase):
    pass


class BiometriaUpdate(BaseModel):
    id_ciclo_estanque: int | None = None
    fecha: date | None = None
    numero_muestra: int | None = Field(default=None, gt=0)
    peso_total_muestra_g: Decimal | None = Field(default=None, gt=0)
    agua_temperatura: Decimal | None = Field(default=None, gt=0)
    agua_salinidad: Decimal | None = Field(default=None, gt=0)
    agua_oxigeno: Decimal | None = Field(default=None, gt=0)
    observaciones: str | None = None


class BiometriaRead(BiometriaBase):
    id_biometria: int
    peso_promedio_g: Decimal
    registrado_por: int
    creado_en: datetime

    model_config = ConfigDict(from_attributes=True)


class BiometriaPredictionRecord(BaseModel):
    numero_biometria: int
    fecha: date
    peso_promedio_predicho: float
    agua_temperatura_predicha: float
    agua_salinidad_predicha: float
    agua_oxigeno_predicho: float
    confianza: float


class BiometriaPredictionResponse(BaseModel):
    ciclo_nombre: str
    estanque_nombre: str
    numero_biometria_actual: int
    fecha_siembra: date
    predicciones: list[BiometriaPredictionRecord]
    r2_modelo: float
    cantidad_datos_entrenamiento: int
