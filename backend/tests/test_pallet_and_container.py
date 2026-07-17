from app.optimization import constants as c
from app.optimization.carton import optimize_carton
from app.optimization.container import optimize_container
from app.optimization.package import optimize_package
from app.optimization.pallet import optimize_pallet
from app.optimization.models import PackageShape, PackagingMaterial


def _carton():
    best, _ = optimize_package(0.45, 250, PackageShape.SQUARE, PackagingMaterial.PAPER)
    return optimize_carton(best, 250)


def test_pallet_height_within_limit():
    pallet = optimize_pallet(_carton())
    assert pallet.pallet_height_mm <= c.MAX_PALLET_HEIGHT_MM


def test_pallet_weight_within_limit():
    pallet = optimize_pallet(_carton())
    assert pallet.total_weight_kg <= c.MAX_PALLET_WEIGHT_KG


def test_cartons_per_pallet_is_layer_times_layers():
    pallet = optimize_pallet(_carton())
    assert pallet.cartons_per_pallet == pallet.cartons_per_layer * pallet.layers


def test_container_recommends_lowest_freight_cost():
    carton = _carton()
    pallet = optimize_pallet(carton)
    result = optimize_container(carton, pallet, total_units_required=50_000)
    all_costs = [result.best.freight_cost] + [a.freight_cost for a in result.alternatives]
    assert result.best.freight_cost == min(all_costs)


def test_container_utilization_between_zero_and_one():
    carton = _carton()
    pallet = optimize_pallet(carton)
    result = optimize_container(carton, pallet, total_units_required=50_000)
    for candidate in [result.best, *result.alternatives]:
        assert 0 <= candidate.utilization <= 1
        assert candidate.empty_space == round(1 - candidate.utilization, 4)


def test_more_units_required_never_decreases_containers_required():
    carton = _carton()
    pallet = optimize_pallet(carton)
    small = optimize_container(carton, pallet, total_units_required=1_000)
    large = optimize_container(carton, pallet, total_units_required=100_000)
    assert large.best.containers_required >= small.best.containers_required
