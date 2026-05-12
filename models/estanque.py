from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from utils.database import Base

if TYPE_CHECKING:
    from models.ciclo_estanque import CicloEstanque


class Estanque(Base):
    __tablename__ = "estanques"

    id_estanque: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    ubicacion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    superficie_m2: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="activo")
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    ciclo_estanques: Mapped[list["CicloEstanque"]] = relationship(
        "CicloEstanque", back_populates="estanque", cascade="all, delete-orphan"
    )
