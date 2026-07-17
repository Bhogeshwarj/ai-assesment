import uuid
from datetime import datetime

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Simulation(Base):
    """One "New Optimization" run: the raw user inputs from Module 2. All
    downstream package/carton/pallet/container/result rows hang off this."""

    __tablename__ = "simulations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    tea_density_g_cm3: Mapped[float] = mapped_column(Float, nullable=False)
    package_weight_g: Mapped[float] = mapped_column(Float, nullable=False)
    shipment_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    shipment_type: Mapped[str] = mapped_column(String(20), nullable=False)
    package_shape: Mapped[str] = mapped_column(String(20), nullable=False)
    packaging_material: Mapped[str] = mapped_column(String(20), nullable=False)
    target_market: Mapped[str | None] = mapped_column(String(120), nullable=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="simulations")
    package_types: Mapped[list["PackageType"]] = relationship(back_populates="simulation", cascade="all, delete-orphan")
    cartons: Mapped[list["Carton"]] = relationship(back_populates="simulation", cascade="all, delete-orphan")
    pallets: Mapped[list["Pallet"]] = relationship(back_populates="simulation", cascade="all, delete-orphan")
    containers: Mapped[list["Container"]] = relationship(back_populates="simulation", cascade="all, delete-orphan")
    result: Mapped["Result"] = relationship(back_populates="simulation", uselist=False, cascade="all, delete-orphan")
