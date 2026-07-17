import pytest

from app.optimization.models import PackageShape, PackagingMaterial, ShipmentType, SimulationInput
from app.optimization.pipeline import run_simulation


@pytest.fixture
def base_input():
    return SimulationInput(
        tea_density_g_cm3=0.45,
        package_weight_g=250,
        shipment_quantity=20_000,
        shipment_type=ShipmentType.TOTAL_WEIGHT,
        package_shape=PackageShape.SQUARE,
        packaging_material=PackagingMaterial.PAPER,
    )


def test_best_scenario_has_lowest_total_cost_among_all_candidates(base_input):
    result = run_simulation(base_input)
    all_costs = [result.best_scenario.total_cost] + [s.total_cost for s in result.alternative_scenarios]
    assert result.best_scenario.total_cost == min(all_costs)


def test_comparison_table_has_all_nine_parameters(base_input):
    result = run_simulation(base_input)
    parameters = {row.parameter for row in result.comparison}
    assert parameters == {
        "Package Size", "Carton Size", "Units Per Carton", "Cartons Per Pallet",
        "Containers Required", "Packaging Cost", "Freight Cost",
        "Container Utilization", "Total Cost",
    }


def test_ai_total_cost_beats_baseline(base_input):
    result = run_simulation(base_input)
    assert result.best_scenario.total_cost < result.baseline_scenario.total_cost


def test_total_units_required_covers_the_requested_weight(base_input):
    result = run_simulation(base_input)
    total_weight_g = result.total_units_required * base_input.package_weight_g
    requested_weight_g = base_input.shipment_quantity * 1000
    # container-loading rounds up to whole containers, so AI capacity should
    # meet or modestly exceed what was actually requested
    assert total_weight_g >= requested_weight_g


def test_per_container_shipment_type(base_input):
    base_input.shipment_type = ShipmentType.PER_CONTAINER
    base_input.shipment_quantity = 2
    result = run_simulation(base_input)
    assert result.best_scenario.container.best.containers_required >= 1


def test_round_shape_end_to_end(base_input):
    base_input.package_shape = PackageShape.ROUND
    base_input.packaging_material = PackagingMaterial.METAL
    result = run_simulation(base_input)
    assert result.best_scenario.package.shape == PackageShape.ROUND
