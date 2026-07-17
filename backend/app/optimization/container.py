"""
Module 6 - Container Optimization.

For each of the three standard container types (20GP, 40GP, 40HC), fit
pallets onto the container floor (best of two footprint orientations),
cap by the container's max payload, then compute how many containers are
needed to move the full required unit count and the resulting freight cost.
The container type with the lowest total freight cost is recommended;
the other two are returned as alternatives for comparison.
"""
import math

from app.optimization import constants as c
from app.optimization.models import CartonResult, ContainerCandidate, ContainerResult, PalletResult


def _evaluate_container_type(container_type: str, pallet: PalletResult, carton: CartonResult,
                              total_units_required: int) -> ContainerCandidate:
    spec = c.CONTAINER_TYPES[container_type]

    orientation_a = math.floor(spec["length"] / c.PALLET_LENGTH_MM) * math.floor(spec["width"] / c.PALLET_WIDTH_MM)
    orientation_b = math.floor(spec["length"] / c.PALLET_WIDTH_MM) * math.floor(spec["width"] / c.PALLET_LENGTH_MM)
    pallets_per_container = max(orientation_a, orientation_b, 0)

    if pallet.pallet_height_mm > spec["height"]:
        pallets_per_container = 0

    if pallet.total_weight_kg > 0:
        max_pallets_by_weight = math.floor(spec["payload_kg"] / pallet.total_weight_kg)
        pallets_per_container = min(pallets_per_container, max_pallets_by_weight)

    pallets_per_container = max(pallets_per_container, 0)
    cartons_per_container = pallets_per_container * pallet.cartons_per_pallet
    units_per_container = cartons_per_container * carton.units_per_carton

    used_volume = pallets_per_container * (c.PALLET_LENGTH_MM * c.PALLET_WIDTH_MM * pallet.pallet_height_mm)
    container_volume = spec["length"] * spec["width"] * spec["height"]
    utilization = used_volume / container_volume if container_volume else 0.0

    containers_required = math.ceil(total_units_required / units_per_container) if units_per_container > 0 else 0
    freight_cost = containers_required * spec["freight_cost"]

    return ContainerCandidate(
        container_type=container_type,
        pallets_per_container=pallets_per_container,
        cartons_per_container=cartons_per_container,
        total_units=units_per_container,
        utilization=round(utilization, 4),
        empty_space=round(1 - utilization, 4),
        containers_required=containers_required,
        freight_cost=round(freight_cost, 2),
    )


def optimize_container(carton: CartonResult, pallet: PalletResult, total_units_required: int) -> ContainerResult:
    candidates = [
        _evaluate_container_type(ct, pallet, carton, total_units_required)
        for ct in c.CONTAINER_TYPES
    ]
    # Only containers that can actually carry at least one unit are viable.
    viable = [cand for cand in candidates if cand.total_units > 0] or candidates
    viable.sort(key=lambda cand: (cand.freight_cost, -cand.utilization))
    best = viable[0]
    alternatives = [cand for cand in candidates if cand.container_type != best.container_type]
    return ContainerResult(best=best, alternatives=alternatives)
