from app.optimization import constants as c
from app.optimization.carton import optimize_carton
from app.optimization.package import optimize_package
from app.optimization.models import PackageShape, PackagingMaterial


def _package(weight_g=250, density=0.45):
    best, _ = optimize_package(density, weight_g, PackageShape.SQUARE, PackagingMaterial.PAPER)
    return best


def test_units_per_carton_is_at_least_one():
    carton = optimize_carton(_package(), 250)
    assert carton.units_per_carton >= 1


def test_carton_respects_handling_weight_limit():
    carton = optimize_carton(_package(weight_g=250), 250)
    assert carton.carton_weight_kg <= c.MAX_CARTON_WEIGHT_KG


def test_carton_respects_max_dimension_plus_padding():
    carton = optimize_carton(_package(), 250)
    max_allowed = c.MAX_CARTON_DIM_MM + c.CARTON_WALL_PADDING_MM
    assert carton.length_mm <= max_allowed
    assert carton.width_mm <= max_allowed
    assert carton.height_mm <= max_allowed


def test_heavier_package_yields_fewer_units_per_carton():
    light_carton = optimize_carton(_package(weight_g=50), 50)
    heavy_carton = optimize_carton(_package(weight_g=1000), 1000)
    assert heavy_carton.units_per_carton <= light_carton.units_per_carton


def test_board_grade_is_selected_from_rule_table():
    carton = optimize_carton(_package(), 250)
    grades = {grade for _, grade, _ in c.BOARD_GRADE_RULES}
    assert carton.board_grade in grades
