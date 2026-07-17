"""Framework-agnostic dataclasses used across the optimization engine.

Kept separate from the API's Pydantic schemas (app/schemas) on purpose: this
package must be importable and unit-testable without FastAPI/DB dependencies.
"""
from dataclasses import dataclass, field
from enum import Enum


class PackageShape(str, Enum):
    SQUARE = "square"
    ROUND = "round"


class PackagingMaterial(str, Enum):
    PAPER = "paper"
    PLASTIC = "plastic"
    METAL = "metal"


class ShipmentType(str, Enum):
    TOTAL_WEIGHT = "total_weight"
    PER_CONTAINER = "per_container"


@dataclass
class SimulationInput:
    tea_density_g_cm3: float
    package_weight_g: float
    shipment_quantity: float
    shipment_type: ShipmentType = ShipmentType.TOTAL_WEIGHT
    package_shape: PackageShape = PackageShape.SQUARE
    packaging_material: PackagingMaterial = PackagingMaterial.PAPER
    target_market: str | None = None


@dataclass
class PackageOption:
    name: str
    shape: PackageShape
    length_mm: float
    width_mm: float
    height_mm: float  # for round packages this is the diameter-equivalent width==length
    product_volume_cm3: float
    package_volume_cm3: float
    fill_ratio: float
    surface_area_m2: float
    material_usage_g: float
    estimated_cost: float
    score: float = 0.0


@dataclass
class CartonResult:
    length_mm: float
    width_mm: float
    height_mm: float
    units_per_carton: int
    carton_weight_kg: float
    board_grade: str
    carton_material_cost: float
    orientation: tuple[int, int, int] = (0, 0, 0)


@dataclass
class PalletResult:
    cartons_per_layer: int
    layers: int
    cartons_per_pallet: int
    pallet_height_mm: float
    total_weight_kg: float


@dataclass
class ContainerCandidate:
    container_type: str
    pallets_per_container: int
    cartons_per_container: int
    total_units: int
    utilization: float
    empty_space: float
    containers_required: int
    freight_cost: float


@dataclass
class ContainerResult:
    best: ContainerCandidate
    alternatives: list[ContainerCandidate] = field(default_factory=list)


@dataclass
class ScenarioResult:
    """One full pipeline run (a candidate package option carried through
    carton -> pallet -> container) with its total landed cost."""
    package: PackageOption
    carton: CartonResult
    pallet: PalletResult
    container: ContainerResult
    packaging_cost_total: float
    freight_cost_total: float
    total_cost: float


@dataclass
class ComparisonRow:
    parameter: str
    current: str
    ai: str
    improvement_pct: float | None


@dataclass
class SimulationResult:
    inputs: SimulationInput
    best_scenario: ScenarioResult
    alternative_scenarios: list[ScenarioResult]
    baseline_scenario: ScenarioResult
    comparison: list[ComparisonRow]
    total_units_required: int
