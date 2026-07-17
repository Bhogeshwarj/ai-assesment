"""
"Current" (manual/non-optimized) baseline, used only to produce the
Module 7 Current-vs-AI comparison. It mirrors the same four stages as the
AI pipeline (package -> carton -> pallet -> container) but makes the same
simplifying, non-optimized choices a human planner typically makes today:

- Package: always a plain cube, sized with a generous fill ratio (lots of
  wasted headspace) instead of a shape-aware, fill-optimized pouch.
- Carton: picked from a small fixed catalog of "standard" box sizes rather
  than sized to the product, and packed at an assumed 70% packing
  efficiency rather than an exact grid.
- Pallet: a fixed rule-of-thumb layer count, not height/weight-optimized.
- Container: always defaults to a 40GP, regardless of what is actually
  cheapest for the shipment.
"""
import math

from app.optimization import constants as c
from app.optimization.container import _evaluate_container_type
from app.optimization.models import CartonResult, PackageOption, PackageShape, PalletResult


def baseline_package(tea_density_g_cm3: float, package_weight_g: float,
                      material) -> PackageOption:
    from app.optimization.package import _material_metrics, _round_up

    product_volume_cm3 = package_weight_g / tea_density_g_cm3
    package_volume_cm3 = product_volume_cm3 / c.BASELINE_FILL_RATIO
    package_volume_mm3 = package_volume_cm3 * 1000
    side = _round_up(package_volume_mm3 ** (1 / 3))
    actual_volume_cm3 = (side ** 3) / 1000
    fill_ratio = product_volume_cm3 / actual_volume_cm3
    surface_area_mm2 = 6 * side * side
    surface_area_m2, material_usage_g, estimated_cost = _material_metrics(surface_area_mm2, material)

    return PackageOption(
        name="current_generic_cube", shape=PackageShape.SQUARE,
        length_mm=side, width_mm=side, height_mm=side,
        product_volume_cm3=round(product_volume_cm3, 2),
        package_volume_cm3=round(actual_volume_cm3, 2),
        fill_ratio=round(fill_ratio, 4),
        surface_area_m2=round(surface_area_m2, 5),
        material_usage_g=round(material_usage_g, 3),
        estimated_cost=round(estimated_cost, 4),
    )


def baseline_carton(package: PackageOption, package_weight_g: float) -> CartonResult:
    package_volume_cm3 = package.package_volume_cm3
    package_weight_kg = package_weight_g / 1000

    # Smallest catalog carton that can fit at least one unit; efficiency
    # factor (not exact grid packing) approximates real-world gaps.
    chosen = None
    for length, width, height in c.BASELINE_CARTONS_MM:
        carton_volume_cm3 = (length * width * height) / 1000
        units = math.floor((carton_volume_cm3 * c.BASELINE_PACKING_EFFICIENCY) / package_volume_cm3)
        if units >= 1:
            chosen = (length, width, height, units)
            break
    if chosen is None:
        length, width, height = c.BASELINE_CARTONS_MM[-1]
        chosen = (length, width, height, 1)

    length, width, height, units = chosen
    contents_weight_kg = units * package_weight_kg
    grade, grammage = "5-ply (Double Wall)", 0.90  # fixed grade, not weight-optimized
    surface_area_m2 = 2 * (length * width + width * height + length * height) / 1_000_000
    tare_weight_kg = surface_area_m2 * grammage
    carton_weight_kg = contents_weight_kg + tare_weight_kg
    carton_material_cost = surface_area_m2 * c.CARTON_MATERIAL_COST_PER_SQM

    return CartonResult(
        length_mm=length, width_mm=width, height_mm=height,
        units_per_carton=units,
        carton_weight_kg=round(carton_weight_kg, 3),
        board_grade=grade,
        carton_material_cost=round(carton_material_cost, 4),
        orientation=(1, 1, units),
    )


def baseline_pallet(carton: CartonResult) -> PalletResult:
    cartons_per_layer = max(1, math.floor(c.PALLET_LENGTH_MM / carton.length_mm) *
                             math.floor(c.PALLET_WIDTH_MM / carton.width_mm))
    layers = c.BASELINE_PALLET_LAYERS
    cartons_per_pallet = cartons_per_layer * layers
    pallet_height_mm = c.PALLET_BASE_HEIGHT_MM + layers * carton.height_mm
    total_weight_kg = c.PALLET_TARE_WEIGHT_KG + cartons_per_pallet * carton.carton_weight_kg

    return PalletResult(
        cartons_per_layer=cartons_per_layer,
        layers=layers,
        cartons_per_pallet=cartons_per_pallet,
        pallet_height_mm=round(pallet_height_mm, 1),
        total_weight_kg=round(total_weight_kg, 2),
    )


def baseline_container(carton: CartonResult, pallet: PalletResult, total_units_required: int):
    return _evaluate_container_type(c.BASELINE_CONTAINER_TYPE, pallet, carton, total_units_required)
