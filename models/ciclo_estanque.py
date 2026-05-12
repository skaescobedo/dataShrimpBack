from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from utils.database import Base

if TYPE_CHECKING:
    from models.biometria import Biometria
    from models.ciclo import Ciclo
    from models.estanque import Estanque


class CicloEstanque(Base):
    __tablename__ = "ciclo_estanques"
    __table_args__ = (UniqueConstraint("id_ciclo", "id_estanque", name="uq_ciclo_estanque"),)

    id_ciclo_estanque: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    id_ciclo: Mapped[int] = mapped_column(ForeignKey("ciclos.id_ciclo"), nullable=False)
    id_estanque: Mapped[int] = mapped_column(ForeignKey("estanques.id_estanque"), nullable=False)
    fecha_siembra: Mapped[date] = mapped_column(Date, nullable=False)
    densidad_inicial_m2: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    peso_inicial_promedio_g: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="activo")

    ciclo: Mapped["Ciclo"] = relationship("Ciclo", back_populates="ciclo_estanques")
    estanque: Mapped["Estanque"] = relationship("Estanque", back_populates="ciclo_estanques")
    biometrias: Mapped[list["Biometria"]] = relationship(
        "Biometria", back_populates="ciclo_estanque", cascade="all, delete-orphan"
    )
