import uuid

from sqlalchemy import Float, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TeaDensityProfile(Base):
    """Lookup table of common tea types and their typical bulk density, so
    the frontend can offer a "pick a tea type" shortcut instead of forcing
    the user to know their density figure. The optimization engine itself
    only ever consumes a raw density number - this table is a convenience
    layer on top of it."""

    __tablename__ = "tea_density_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    density_g_cm3: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)


class PackagingMaterialRef(Base):
    """Lookup table backing the Packaging Material dropdown (paper/plastic/
    metal) and the cost/weight assumptions the engine uses for that
    material. Mirrors app/optimization/constants.py::MATERIAL_PROPERTIES so
    those figures can be edited by an admin without a code deploy."""

    __tablename__ = "packaging_materials"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    cost_per_sqm: Mapped[float] = mapped_column(Float, nullable=False)
    thickness_mm: Mapped[float] = mapped_column(Float, nullable=False)
    density_g_cm3: Mapped[float] = mapped_column(Float, nullable=False)
