"""Thin wrappers around the optimization engine for the granular
/optimize/package, /optimize/carton, /optimize/pallet, /optimize/container
endpoints. Each of these operates on a single stage in isolation (no
persistence) - useful for a frontend that wants to let a user tweak one
stage at a time, and for testing each stage of the pipeline independently."""
from app.optimization.carton import optimize_carton
from app.optimization.container import optimize_container
from app.optimization.models import CartonResult, PackageOption, PackageShape, PalletResult
from app.optimization.package import optimize_package
from app.optimization.pallet import optimize_pallet
from app.schemas.optimization import (
    CartonOptimizeRequest,
    ContainerOptimizeRequest,
    PackageOptimizeRequest,
    PalletOptimizeRequest,
)


def run_package_optimization(request: PackageOptimizeRequest):
    best, alternatives = optimize_package(
        request.tea_density_g_cm3, request.package_weight_g, request.package_shape, request.packaging_material
    )
    return best, alternatives


def run_carton_optimization(request: CartonOptimizeRequest) -> CartonResult:
    package = PackageOption(
        name="user_supplied", shape=PackageShape.SQUARE,
        length_mm=request.package_length_mm, width_mm=request.package_width_mm, height_mm=request.package_height_mm,
        product_volume_cm3=0, package_volume_cm3=0, fill_ratio=0, surface_area_m2=0,
        material_usage_g=0, estimated_cost=0,
    )
    return optimize_carton(package, request.package_weight_g)


def run_pallet_optimization(request: PalletOptimizeRequest) -> PalletResult:
    carton = CartonResult(
        length_mm=request.carton_length_mm, width_mm=request.carton_width_mm, height_mm=request.carton_height_mm,
        units_per_carton=0, carton_weight_kg=request.carton_weight_kg, board_grade="", carton_material_cost=0,
    )
    return optimize_pallet(carton)


def run_container_optimization(request: ContainerOptimizeRequest):
    carton = CartonResult(
        length_mm=0, width_mm=0, height_mm=0, units_per_carton=request.carton_units_per_carton,
        carton_weight_kg=0, board_grade="", carton_material_cost=0,
    )
    pallet = PalletResult(
        cartons_per_layer=0, layers=0, cartons_per_pallet=request.cartons_per_pallet,
        pallet_height_mm=request.pallet_height_mm, total_weight_kg=request.pallet_total_weight_kg,
    )
    return optimize_container(carton, pallet, request.total_units_required)
