"""
Orchestrates the full AI Logic pipeline described in the brief:

    Tea Density -> Volume -> Package Options -> Optimize Carton ->
    Optimize Pallet -> Optimize Container -> Compare Multiple Scenarios ->
    Recommend Lowest Cost Solution

Every package candidate produced by `optimize_package` is carried all the
way through to a full landed-cost figure (packaging material + freight),
and the scenario with the lowest total cost is recommended - not simply the
package with the best fill ratio. This is the "compare scenarios, recommend
lowest cost" step from the brief.

A parallel non-optimized "baseline" pipeline (see baseline.py) is run once
to produce the Module 7 Current-vs-AI comparison.
"""
import math

from app.optimization import constants as c
from app.optimization.baseline import baseline_carton, baseline_container, baseline_package, baseline_pallet
from app.optimization.carton import optimize_carton
from app.optimization.container import optimize_container
from app.optimization.models import (
    ComparisonRow, ContainerResult, ScenarioResult, SimulationInput, SimulationResult, ShipmentType,
)
from app.optimization.package import optimize_package
from app.optimization.pallet import optimize_pallet


def _dims(length: float, width: float, height: float) -> str:
    return f"{length:.0f} x {width:.0f} x {height:.0f} mm"


def _pct_improvement(current: float, ai: float, higher_is_better: bool) -> float | None:
    if current == 0:
        return None
    if higher_is_better:
        return round((ai - current) / current * 100, 2)
    return round((current - ai) / current * 100, 2)


def _units_required_for_container(candidate_units_per_container: int, shipment_quantity: float,
                                   shipment_type: ShipmentType, package_weight_g: float) -> int:
    if shipment_type == ShipmentType.PER_CONTAINER:
        return max(1, math.ceil(shipment_quantity * candidate_units_per_container))
    total_weight_g = shipment_quantity * 1000  # shipment_quantity given in kg
    return max(1, math.ceil(total_weight_g / package_weight_g))


def _build_scenario(package, inputs: SimulationInput) -> ScenarioResult:
    carton = optimize_carton(package, inputs.package_weight_g)
    pallet = optimize_pallet(carton)

    # Capacity per container is independent of demand; run once with a
    # placeholder demand of 1 unit to discover per-container capacity, then
    # recompute with the real demand once it's known (for PER_CONTAINER
    # shipments the demand itself depends on that capacity).
    probe = optimize_container(carton, pallet, total_units_required=1)
    units_per_container = probe.best.total_units or 1
    total_units_required = _units_required_for_container(
        units_per_container, inputs.shipment_quantity, inputs.shipment_type, inputs.package_weight_g
    )
    container = optimize_container(carton, pallet, total_units_required)

    total_cartons_required = math.ceil(total_units_required / carton.units_per_carton)
    packaging_cost_total = (
        total_units_required * package.estimated_cost
        + total_cartons_required * carton.carton_material_cost
    )
    freight_cost_total = container.best.freight_cost
    total_cost = packaging_cost_total + freight_cost_total

    return ScenarioResult(
        package=package, carton=carton, pallet=pallet, container=container,
        packaging_cost_total=round(packaging_cost_total, 2),
        freight_cost_total=round(freight_cost_total, 2),
        total_cost=round(total_cost, 2),
    )


def _build_baseline_scenario(inputs: SimulationInput) -> ScenarioResult:
    package = baseline_package(inputs.tea_density_g_cm3, inputs.package_weight_g, inputs.packaging_material)
    carton = baseline_carton(package, inputs.package_weight_g)
    pallet = baseline_pallet(carton)

    probe = baseline_container(carton, pallet, total_units_required=1)
    units_per_container = probe.total_units or 1
    total_units_required = _units_required_for_container(
        units_per_container, inputs.shipment_quantity, inputs.shipment_type, inputs.package_weight_g
    )
    best_candidate = baseline_container(carton, pallet, total_units_required)
    container = ContainerResult(best=best_candidate, alternatives=[])

    total_cartons_required = math.ceil(total_units_required / carton.units_per_carton)
    packaging_cost_total = (
        total_units_required * package.estimated_cost
        + total_cartons_required * carton.carton_material_cost
    )
    freight_cost_total = container.best.freight_cost
    total_cost = packaging_cost_total + freight_cost_total

    return ScenarioResult(
        package=package, carton=carton, pallet=pallet, container=container,
        packaging_cost_total=round(packaging_cost_total, 2),
        freight_cost_total=round(freight_cost_total, 2),
        total_cost=round(total_cost, 2),
    )


def _build_comparison(current: ScenarioResult, ai: ScenarioResult) -> list[ComparisonRow]:
    rows = [
        ComparisonRow(
            "Package Size",
            _dims(current.package.length_mm, current.package.width_mm, current.package.height_mm),
            _dims(ai.package.length_mm, ai.package.width_mm, ai.package.height_mm),
            _pct_improvement(current.package.package_volume_cm3, ai.package.package_volume_cm3, higher_is_better=False),
        ),
        ComparisonRow(
            "Carton Size",
            _dims(current.carton.length_mm, current.carton.width_mm, current.carton.height_mm),
            _dims(ai.carton.length_mm, ai.carton.width_mm, ai.carton.height_mm),
            None,
        ),
        ComparisonRow(
            "Units Per Carton", str(current.carton.units_per_carton), str(ai.carton.units_per_carton),
            _pct_improvement(current.carton.units_per_carton, ai.carton.units_per_carton, higher_is_better=True),
        ),
        ComparisonRow(
            "Cartons Per Pallet", str(current.pallet.cartons_per_pallet), str(ai.pallet.cartons_per_pallet),
            # Raw carton counts aren't directly comparable when carton sizes
            # differ (fewer, larger cartons can still hold far more product) -
            # so the improvement figure here is based on *units per pallet*
            # (cartons_per_pallet x units_per_carton), the true density metric.
            _pct_improvement(
                current.pallet.cartons_per_pallet * current.carton.units_per_carton,
                ai.pallet.cartons_per_pallet * ai.carton.units_per_carton,
                higher_is_better=True,
            ),
        ),
        ComparisonRow(
            "Containers Required", str(current.container.best.containers_required),
            str(ai.container.best.containers_required),
            _pct_improvement(current.container.best.containers_required, ai.container.best.containers_required,
                              higher_is_better=False),
        ),
        ComparisonRow(
            "Packaging Cost", f"${current.packaging_cost_total:,.2f}", f"${ai.packaging_cost_total:,.2f}",
            _pct_improvement(current.packaging_cost_total, ai.packaging_cost_total, higher_is_better=False),
        ),
        ComparisonRow(
            "Freight Cost", f"${current.freight_cost_total:,.2f}", f"${ai.freight_cost_total:,.2f}",
            _pct_improvement(current.freight_cost_total, ai.freight_cost_total, higher_is_better=False),
        ),
        ComparisonRow(
            "Container Utilization", f"{current.container.best.utilization * 100:.1f}%",
            f"{ai.container.best.utilization * 100:.1f}%",
            _pct_improvement(current.container.best.utilization, ai.container.best.utilization, higher_is_better=True),
        ),
        ComparisonRow(
            "Total Cost", f"${current.total_cost:,.2f}", f"${ai.total_cost:,.2f}",
            _pct_improvement(current.total_cost, ai.total_cost, higher_is_better=False),
        ),
    ]
    return rows


def run_simulation(inputs: SimulationInput) -> SimulationResult:
    _, package_candidates = optimize_package(
        inputs.tea_density_g_cm3, inputs.package_weight_g, inputs.package_shape, inputs.packaging_material
    )

    scenarios = [_build_scenario(pkg, inputs) for pkg in package_candidates]
    scenarios.sort(key=lambda s: s.total_cost)
    best_scenario, alternative_scenarios = scenarios[0], scenarios[1:]

    baseline_scenario = _build_baseline_scenario(inputs)
    comparison = _build_comparison(baseline_scenario, best_scenario)

    total_units_required = (
        best_scenario.container.best.containers_required * best_scenario.container.best.total_units
    )

    return SimulationResult(
        inputs=inputs,
        best_scenario=best_scenario,
        alternative_scenarios=alternative_scenarios,
        baseline_scenario=baseline_scenario,
        comparison=comparison,
        total_units_required=total_units_required,
    )
