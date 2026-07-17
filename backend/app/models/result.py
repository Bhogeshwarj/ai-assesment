import uuid
from datetime import datetime

from sqlalchemy import Float, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Result(Base):
    """Module 7 - the aggregated Current-vs-AI comparison for a simulation,
    persisted so the Dashboard/History pages can list past results without
    re-running the optimization pipeline."""

    __tablename__ = "results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    simulation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("simulations.id"), unique=True, nullable=False)

    total_units_required: Mapped[int] = mapped_column(Integer, nullable=False)

    packaging_cost_current: Mapped[float] = mapped_column(Float, nullable=False)
    packaging_cost_ai: Mapped[float] = mapped_column(Float, nullable=False)
    freight_cost_current: Mapped[float] = mapped_column(Float, nullable=False)
    freight_cost_ai: Mapped[float] = mapped_column(Float, nullable=False)
    total_cost_current: Mapped[float] = mapped_column(Float, nullable=False)
    total_cost_ai: Mapped[float] = mapped_column(Float, nullable=False)

    total_savings: Mapped[float] = mapped_column(Float, nullable=False)
    savings_pct: Mapped[float] = mapped_column(Float, nullable=False)
    container_utilization_current: Mapped[float] = mapped_column(Float, nullable=False)
    container_utilization_ai: Mapped[float] = mapped_column(Float, nullable=False)

    # Full ComparisonRow table (Module 7) stored verbatim for fast reads.
    comparison_table: Mapped[list[dict]] = mapped_column(JSONB, nullable=False)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    simulation: Mapped["Simulation"] = relationship(back_populates="result")
