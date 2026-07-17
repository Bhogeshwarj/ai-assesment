import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.simulation import Simulation
from app.models.result import Result
from app.optimization.models import SimulationResult
from app.schemas.optimization import (
    CompareResponse,
    SimulationInputSchema,
    SimulationListItem,
    SimulationResponse,
    SimulationResultSchema,
)
from app.optimization.models import SimulationInput
from app.optimization.pipeline import run_simulation
from app.services import simulation_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["simulations"])


def _to_response(simulation: Simulation, result: SimulationResult) -> SimulationResponse:
    base = SimulationResultSchema.model_validate(result, from_attributes=True)
    return SimulationResponse(
        id=str(simulation.id),
        created_at=simulation.created_at.isoformat(),
        **base.model_dump(),
    )


def _to_list_item(simulation: Simulation, result_row: Result) -> SimulationListItem:
    return SimulationListItem(
        id=str(simulation.id),
        created_at=simulation.created_at.isoformat(),
        tea_density_g_cm3=simulation.tea_density_g_cm3,
        package_weight_g=simulation.package_weight_g,
        shipment_quantity=simulation.shipment_quantity,
        total_cost_ai=result_row.total_cost_ai,
        total_savings=result_row.total_savings,
        savings_pct=result_row.savings_pct,
        container_utilization_ai=result_row.container_utilization_ai,
    )


@router.post("/simulation", response_model=SimulationResponse, status_code=201)
def create_simulation(payload: SimulationInputSchema, db: Session = Depends(get_db)) -> SimulationResponse:
    """Runs the full AI Logic pipeline (Modules 2-7) and persists the run."""
    simulation, result = simulation_service.create_simulation(db, payload)
    return _to_response(simulation, result)


@router.get("/simulation", response_model=list[SimulationListItem])
def list_simulations(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[SimulationListItem]:
    """Module 1 / History page - list past simulations, most recent first."""
    rows = simulation_service.list_simulations(db, limit=limit, offset=offset)
    return [_to_list_item(sim, res) for sim, res in rows]


@router.get("/simulation/{simulation_id}", response_model=SimulationResponse)
def get_simulation(simulation_id: uuid.UUID, db: Session = Depends(get_db)) -> SimulationResponse:
    found = simulation_service.get_simulation(db, simulation_id)
    if found is None:
        raise HTTPException(status_code=404, detail=f"Simulation {simulation_id} not found")
    simulation, result = found
    return _to_response(simulation, result)


@router.post("/compare", response_model=CompareResponse)
def compare(payload: SimulationInputSchema) -> CompareResponse:
    """Module 7 - Current vs AI Comparison, computed on the fly (not
    persisted) for a given set of inputs. Use POST /simulation instead if
    the run should be saved to History."""
    inputs = SimulationInput(
        tea_density_g_cm3=payload.tea_density_g_cm3,
        package_weight_g=payload.package_weight_g,
        shipment_quantity=payload.shipment_quantity,
        shipment_type=payload.shipment_type,
        package_shape=payload.package_shape,
        packaging_material=payload.packaging_material,
        target_market=payload.target_market,
    )
    result = run_simulation(inputs)
    total_savings = result.baseline_scenario.total_cost - result.best_scenario.total_cost
    savings_pct = (
        (total_savings / result.baseline_scenario.total_cost * 100) if result.baseline_scenario.total_cost else 0.0
    )
    return CompareResponse(
        inputs=payload,
        comparison=[row.__dict__ for row in result.comparison],
        total_savings=round(total_savings, 2),
        savings_pct=round(savings_pct, 2),
    )


@router.get("/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db)) -> dict:
    """Module 1 - Dashboard. Not one of the 8 minimum endpoints but needed
    to power the Dashboard page's aggregate stat tiles cheaply."""
    summary = simulation_service.dashboard_summary(db)
    summary["recent_simulations"] = [_to_list_item(sim, res) for sim, res in summary["recent_simulations"]]
    return summary
