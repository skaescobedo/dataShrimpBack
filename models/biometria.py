from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from utils.database import Base

if TYPE_CHECKING:
    from models.ciclo_estanque import CicloEstanque
    from models.usuario import Usuario


class Biometria(Base):
    __tablename__ = "biometrias"

    id_biometria: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    id_ciclo_estanque: Mapped[int] = mapped_column(
        ForeignKey("ciclo_estanques.id_ciclo_estanque"), nullable=False
    )
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    numero_muestra: Mapped[int] = mapped_column(Integer, nullable=False)
    peso_total_muestra_g: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    peso_promedio_g: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    registrado_por: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuario"), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    ciclo_estanque: Mapped["CicloEstanque"] = relationship("CicloEstanque", back_populates="biometrias")
    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="biometrias")
