"""Persistence + orchestration for the full simulation pipeline (Modules 1-7).

Design note (documented as an assumption in the README): the optimization
engine is a pure function of its inputs, so GET endpoints recompute the full
nested result from the four stored input scalars rather than deserializing
it back out of the normalized package_types/cartons/pallets/containers
tables. Those tables are still populated on every POST /simulation for
audit/reporting/export use (e.g. a future "download all cartons ever
recommended" report), and the aggregated Result row is used to serve
GET /simulation list/dashboard queries cheaply without recomputation.
"""
import logging
import uuid

from sqlalchemy.orm import Session

from app.models.packaging import Carton, Container, PackageType, Pallet
from app.models.simulation import Simulation
from app.models.result import Result
from app.optimization.models import SimulationInput, SimulationResult
from app.optimization.pipeline import run_simulation
from app.schemas.optimization import SimulationInputSchema

logger = logging.getLogger(__name__)


def _to_input_dataclass(payload: SimulationInputSchema) -> SimulationInput:
    return SimulationInput(
        tea_density_g_cm3=payload.tea_density_g_cm3,
        package_weight_g=payload.package_weight_g,
        shipment_quantity=payload.shipment_quantity,
        shipment_type=payload.shipment_type,
        package_shape=payload.package_shape,
        packaging_material=payload.packaging_material,
        target_market=payload.target_market,
    )


def _persist_scenario(db: Session, simulation_id: uuid.UUID, scenario, *, is_baseline: bool, scenario_rank: int | None,
                       is_recommended: bool = False) -> None:
    package_row = PackageType(
        simulation_id=simulation_id,
        name=scenario.package.name, shape=scenario.package.shape.value,
        length_mm=scenario.package.length_mm, width_mm=scenario.package.width_mm, height_mm=scenario.package.height_mm,
        product_volume_cm3=scenario.package.product_volume_cm3, package_volume_cm3=scenario.package.package_volume_cm3,
        fill_ratio=scenario.package.fill_ratio, surface_area_m2=scenario.package.surface_area_m2,
        material_usage_g=scenario.package.material_usage_g, estimated_cost=scenario.package.estimated_cost,
        is_baseline=is_baseline, scenario_rank=scenario_rank,
    )
    db.add(package_row)
    db.flush()

    carton_row = Carton(
        simulation_id=simulation_id, package_type_id=package_row.id,
        length_mm=scenario.carton.length_mm, width_mm=scenario.carton.width_mm, height_mm=scenario.carton.height_mm,
        units_per_carton=scenario.carton.units_per_carton, carton_weight_kg=scenario.carton.carton_weight_kg,
        board_grade=scenario.carton.board_grade, carton_material_cost=scenario.carton.carton_material_cost,
        is_baseline=is_baseline, scenario_rank=scenario_rank,
    )
    db.add(carton_row)
    db.flush()

    pallet_row = Pallet(
        simulation_id=simulation_id, carton_id=carton_row.id,
        cartons_per_layer=scenario.pallet.cartons_per_layer, layers=scenario.pallet.layers,
        cartons_per_pallet=scenario.pallet.cartons_per_pallet, pallet_height_mm=scenario.pallet.pallet_height_mm,
        total_weight_kg=scenario.pallet.total_weight_kg,
        is_baseline=is_baseline, scenario_rank=scenario_rank,
    )
    db.add(pallet_row)
    db.flush()

    best = scenario.container.best
    db.add(Container(
        simulation_id=simulation_id, pallet_id=pallet_row.id,
        container_type=best.container_type, pallets_per_container=best.pallets_per_container,
        cartons_per_container=best.cartons_per_container, total_units=best.total_units,
        utilization=best.utilization, empty_space=best.empty_space,
        containers_required=best.containers_required, freight_cost=best.freight_cost,
        is_baseline=is_baseline, is_recommended=is_recommended, scenario_rank=scenario_rank,
    ))


def create_simulation(db: Session, payload: SimulationInputSchema) -> tuple[Simulation, SimulationResult]:
    inputs = _to_input_dataclass(payload)
    result = run_simulation(inputs)

    simulation = Simulation(
        tea_density_g_cm3=payload.tea_density_g_cm3,
        package_weight_g=payload.package_weight_g,
        shipment_quantity=payload.shipment_quantity,
        shipment_type=payload.shipment_type.value,
        package_shape=payload.package_shape.value,
        packaging_material=payload.packaging_material.value,
        target_market=payload.target_market,
    )
    db.add(simulation)
    db.flush()

    _persist_scenario(db, simulation.id, result.baseline_scenario, is_baseline=True, scenario_rank=None)
    _persist_scenario(db, simulation.id, result.best_scenario, is_baseline=False, scenario_rank=0, is_recommended=True)
    for rank, alt in enumerate(result.alternative_scenarios, start=1):
        _persist_scenario(db, simulation.id, alt, is_baseline=False, scenario_rank=rank)

    total_savings = result.baseline_scenario.total_cost - result.best_scenario.total_cost
    savings_pct = (total_savings / result.baseline_scenario.total_cost * 100) if result.baseline_scenario.total_cost else 0.0

    db.add(Result(
        simulation_id=simulation.id,
        total_units_required=result.total_units_required,
        packaging_cost_current=result.baseline_scenario.packaging_cost_total,
        packaging_cost_ai=result.best_scenario.packaging_cost_total,
        freight_cost_current=result.baseline_scenario.freight_cost_total,
        freight_cost_ai=result.best_scenario.freight_cost_total,
        total_cost_current=result.baseline_scenario.total_cost,
        total_cost_ai=result.best_scenario.total_cost,
        total_savings=round(total_savings, 2),
        savings_pct=round(savings_pct, 2),
        container_utilization_current=result.baseline_scenario.container.best.utilization,
        container_utilization_ai=result.best_scenario.container.best.utilization,
        comparison_table=[row.__dict__ for row in result.comparison],
    ))

    db.commit()
    db.refresh(simulation)
    logger.info("simulation created id=%s total_savings=%.2f savings_pct=%.1f%%", simulation.id, total_savings, savings_pct)
    return simulation, result


def get_simulation(db: Session, simulation_id: uuid.UUID) -> tuple[Simulation, SimulationResult] | None:
    simulation = db.get(Simulation, simulation_id)
    if simulation is None:
        return None
    inputs = SimulationInput(
        tea_density_g_cm3=simulation.tea_density_g_cm3,
        package_weight_g=simulation.package_weight_g,
        shipment_quantity=simulation.shipment_quantity,
        shipment_type=simulation.shipment_type,
        package_shape=simulation.package_shape,
        packaging_material=simulation.packaging_material,
        target_market=simulation.target_market,
    )
    result = run_simulation(inputs)
    return simulation, result


def list_simulations(db: Session, limit: int = 50, offset: int = 0) -> list[tuple[Simulation, Result]]:
    rows = (
        db.query(Simulation, Result)
        .join(Result, Result.simulation_id == Simulation.id)
        .order_by(Simulation.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return rows


def dashboard_summary(db: Session) -> dict:
    results = db.query(Result).all()
    total_simulations = len(results)
    total_savings = sum(r.total_savings for r in results)
    avg_utilization = (
        sum(r.container_utilization_ai for r in results) / total_simulations if total_simulations else 0.0
    )
    recent = (
        db.query(Simulation, Result)
        .join(Result, Result.simulation_id == Simulation.id)
        .order_by(Simulation.created_at.desc())
        .limit(5)
        .all()
    )
    return {
        "total_simulations": total_simulations,
        "total_savings": round(total_savings, 2),
        "average_container_utilization": round(avg_utilization, 4),
        "recent_simulations": recent,
    }
