import uuid

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PackageType(Base):
    """A candidate inner-pouch/tin option (Module 3) produced for a
    simulation. `is_baseline` marks the non-optimized "current" package;
    among the AI candidates, `scenario_rank` 0 is the recommended one and
    higher ranks are the alternative options shown to the user."""

    __tablename__ = "package_types"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    simulation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("simulations.id"), nullable=False)

    name: Mapped[str] = mapped_column(String(50), nullable=False)
    shape: Mapped[str] = mapped_column(String(20), nullable=False)
    length_mm: Mapped[float] = mapped_column(Float, nullable=False)
    width_mm: Mapped[float] = mapped_column(Float, nullable=False)
    height_mm: Mapped[float] = mapped_column(Float, nullable=False)
    product_volume_cm3: Mapped[float] = mapped_column(Float, nullable=False)
    package_volume_cm3: Mapped[float] = mapped_column(Float, nullable=False)
    fill_ratio: Mapped[float] = mapped_column(Float, nullable=False)
    surface_area_m2: Mapped[float] = mapped_column(Float, nullable=False)
    material_usage_g: Mapped[float] = mapped_column(Float, nullable=False)
    estimated_cost: Mapped[float] = mapped_column(Float, nullable=False)

    is_baseline: Mapped[bool] = mapped_column(Boolean, default=False)
    scenario_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)

    simulation: Mapped["Simulation"] = relationship(back_populates="package_types")
    carton: Mapped["Carton"] = relationship(back_populates="package_type", uselist=False)


class Carton(Base):
    """Module 4 - the master carton sized around a PackageType."""

    __tablename__ = "cartons"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    simulation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("simulations.id"), nullable=False)
    package_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("package_types.id"), nullable=False)

    length_mm: Mapped[float] = mapped_column(Float, nullable=False)
    width_mm: Mapped[float] = mapped_column(Float, nullable=False)
    height_mm: Mapped[float] = mapped_column(Float, nullable=False)
    units_per_carton: Mapped[int] = mapped_column(Integer, nullable=False)
    carton_weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    board_grade: Mapped[str] = mapped_column(String(50), nullable=False)
    carton_material_cost: Mapped[float] = mapped_column(Float, nullable=False)

    is_baseline: Mapped[bool] = mapped_column(Boolean, default=False)
    scenario_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)

    simulation: Mapped["Simulation"] = relationship(back_populates="cartons")
    package_type: Mapped["PackageType"] = relationship(back_populates="carton")
    pallet: Mapped["Pallet"] = relationship(back_populates="carton", uselist=False)


class Pallet(Base):
    """Module 5 - pallet loading for a given carton."""

    __tablename__ = "pallets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    simulation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("simulations.id"), nullable=False)
    carton_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cartons.id"), nullable=False)

    cartons_per_layer: Mapped[int] = mapped_column(Integer, nullable=False)
    layers: Mapped[int] = mapped_column(Integer, nullable=False)
    cartons_per_pallet: Mapped[int] = mapped_column(Integer, nullable=False)
    pallet_height_mm: Mapped[float] = mapped_column(Float, nullable=False)
    total_weight_kg: Mapped[float] = mapped_column(Float, nullable=False)

    is_baseline: Mapped[bool] = mapped_column(Boolean, default=False)
    scenario_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)

    simulation: Mapped["Simulation"] = relationship(back_populates="pallets")
    carton: Mapped["Carton"] = relationship(back_populates="pallet")
    container: Mapped["Container"] = relationship(back_populates="pallet", uselist=False)


class Container(Base):
    """Module 6 - the recommended container type and its alternatives for a
    given pallet configuration."""

    __tablename__ = "containers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    simulation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("simulations.id"), nullable=False)
    pallet_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pallets.id"), nullable=False)

    container_type: Mapped[str] = mapped_column(String(10), nullable=False)
    pallets_per_container: Mapped[int] = mapped_column(Integer, nullable=False)
    cartons_per_container: Mapped[int] = mapped_column(Integer, nullable=False)
    total_units: Mapped[int] = mapped_column(Integer, nullable=False)
    utilization: Mapped[float] = mapped_column(Float, nullable=False)
    empty_space: Mapped[float] = mapped_column(Float, nullable=False)
    containers_required: Mapped[int] = mapped_column(Integer, nullable=False)
    freight_cost: Mapped[float] = mapped_column(Float, nullable=False)

    is_baseline: Mapped[bool] = mapped_column(Boolean, default=False)
    is_recommended: Mapped[bool] = mapped_column(Boolean, default=False)
    scenario_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)

    simulation: Mapped["Simulation"] = relationship(back_populates="containers")
    pallet: Mapped["Pallet"] = relationship(back_populates="container")
