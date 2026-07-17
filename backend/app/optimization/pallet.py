"""
Module 5 - Pallet Optimization.

Given a carton's footprint and weight, lay cartons out on a standard ISO
pallet: try both footprint orientations against the pallet's length/width
and keep whichever packs more cartons per layer, then stack layers up to
the lower of the height limit and the weight limit.
"""
import math

from app.optimization import constants as c
from app.optimization.models import CartonResult, PalletResult


def optimize_pallet(carton: CartonResult) -> PalletResult:
    orientation_a = math.floor(c.PALLET_LENGTH_MM / carton.length_mm) * math.floor(c.PALLET_WIDTH_MM / carton.width_mm)
    orientation_b = math.floor(c.PALLET_LENGTH_MM / carton.width_mm) * math.floor(c.PALLET_WIDTH_MM / carton.length_mm)
    cartons_per_layer = max(orientation_a, orientation_b, 1)

    max_layers_by_height = max(1, math.floor(
        (c.MAX_PALLET_HEIGHT_MM - c.PALLET_BASE_HEIGHT_MM) / carton.height_mm
    ))
    max_layers_by_weight = max(1, math.floor(
        (c.MAX_PALLET_WEIGHT_KG - c.PALLET_TARE_WEIGHT_KG) / (cartons_per_layer * carton.carton_weight_kg)
    ))
    layers = max(1, min(max_layers_by_height, max_layers_by_weight))

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
