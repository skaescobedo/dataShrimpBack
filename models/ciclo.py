from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from utils.database import Base

if TYPE_CHECKING:
    from models.ciclo_estanque import CicloEstanque


class Ciclo(Base):
    __tablename__ = "ciclos"

    id_ciclo: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[date | None] = mapped_column(Date, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="activo")
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    ciclo_estanques: Mapped[list["CicloEstanque"]] = relationship(
        "CicloEstanque", back_populates="ciclo", cascade="all, delete-orphan"
    )
