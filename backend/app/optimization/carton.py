"""
Module 4 - Carton Optimization.

Instead of picking from a fixed catalog of carton sizes and living with
whatever gaps result (the "current"/manual approach - see baseline.py), the
AI approach sizes the master carton *around* the chosen package: it searches
every axis-aligned orientation of the package and every (nx, ny, nz) grid
count up to the manual-handling dimension/weight limits, and keeps the
orientation+grid that packs the most units with (by construction) zero
wasted volume beyond flap padding.
"""
import math

from app.optimization import constants as c
from app.optimization.models import CartonResult, PackageOption


def _board_grade(contents_weight_kg: float) -> tuple[str, float]:
    for threshold, grade, grammage in c.BOARD_GRADE_RULES:
        if contents_weight_kg <= threshold:
            return grade, grammage
    return c.BOARD_GRADE_RULES[-1][1], c.BOARD_GRADE_RULES[-1][2]


def _best_grid_for_orientation(a: float, b: float, dim: float, package_weight_kg: float) -> tuple[int, int, int]:
    """Given one orientation (a, b, dim) of the package's three axes, find the
    grid count (nx, ny, nz) that maximizes nx*ny*nz subject to the max carton
    external dimension and max carton weight."""
    usable = c.MAX_CARTON_DIM_MM - c.CARTON_WALL_PADDING_MM
    nx = max(1, math.floor(usable / a))
    ny = max(1, math.floor(usable / b))
    nz = max(1, math.floor(usable / dim))

    weight_budget_kg = c.MAX_CARTON_WEIGHT_KG * c.CARTON_CONTENTS_WEIGHT_BUDGET_FRACTION
    max_units_by_weight = max(1, math.floor(weight_budget_kg / package_weight_kg))
    # Greedily shrink the largest axis count until the weight limit is met.
    while nx * ny * nz > max_units_by_weight and (nx > 1 or ny > 1 or nz > 1):
        if nx >= ny and nx >= nz and nx > 1:
            nx -= 1
        elif ny >= nz and ny > 1:
            ny -= 1
        elif nz > 1:
            nz -= 1
        else:
            break
    return nx, ny, nz


def optimize_carton(package: PackageOption, package_weight_g: float) -> CartonResult:
    package_weight_kg = package_weight_g / 1000
    dims = (package.length_mm, package.width_mm, package.height_mm)

    # All 6 axis-aligned orientations of the package inside the carton.
    orientations = [
        (dims[0], dims[1], dims[2]),
        (dims[0], dims[2], dims[1]),
        (dims[1], dims[0], dims[2]),
        (dims[1], dims[2], dims[0]),
        (dims[2], dims[0], dims[1]),
        (dims[2], dims[1], dims[0]),
    ]

    best = None
    for orientation in orientations:
        a, b, dim = orientation
        nx, ny, nz = _best_grid_for_orientation(a, b, dim, package_weight_kg)
        units = nx * ny * nz
        carton_length = nx * a + c.CARTON_WALL_PADDING_MM
        carton_width = ny * b + c.CARTON_WALL_PADDING_MM
        carton_height = nz * dim + c.CARTON_WALL_PADDING_MM
        carton_volume = carton_length * carton_width * carton_height
        candidate = (units, -carton_volume, orientation, (nx, ny, nz),
                     carton_length, carton_width, carton_height)
        if best is None or candidate[:2] > best[:2]:
            best = candidate

    units, _, orientation, grid, length, width, height = best
    contents_weight_kg = units * package_weight_kg
    board_grade, grammage = _board_grade(contents_weight_kg)
    surface_area_m2 = 2 * (length * width + width * height + length * height) / 1_000_000
    tare_weight_kg = surface_area_m2 * grammage
    carton_weight_kg = contents_weight_kg + tare_weight_kg
    carton_material_cost = surface_area_m2 * c.CARTON_MATERIAL_COST_PER_SQM

    return CartonResult(
        length_mm=round(length, 1),
        width_mm=round(width, 1),
        height_mm=round(height, 1),
        units_per_carton=units,
        carton_weight_kg=round(carton_weight_kg, 3),
        board_grade=board_grade,
        carton_material_cost=round(carton_material_cost, 4),
        orientation=grid,
    )
