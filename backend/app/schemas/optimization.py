"""Pydantic schemas shared by both the granular /optimize/* endpoints and the
full /simulation and /compare endpoints. Kept separate from
app/optimization/models.py (plain dataclasses) so the optimization engine
has zero dependency on the web framework."""
from pydantic import BaseModel, Field

from app.optimization.models import PackageShape, PackagingMaterial, ShipmentType


class SimulationInputSchema(BaseModel):
    tea_density_g_cm3: float = Field(..., gt=0, description="Bulk density of the tea in g/cm3")
    package_weight_g: float = Field(..., gt=0, description="Net tea weight per inner package, in grams")
    shipment_quantity: float = Field(..., gt=0, description="Total weight in kg, or number of containers, per shipment_type")
    shipment_type: ShipmentType = ShipmentType.TOTAL_WEIGHT
    package_shape: PackageShape = PackageShape.SQUARE
    packaging_material: PackagingMaterial = PackagingMaterial.PAPER
    target_market: str | None = None

    model_config = {"from_attributes": True}


class PackageOptionSchema(BaseModel):
    name: str
    shape: PackageShape
    length_mm: float
    width_mm: float
    height_mm: float
    product_volume_cm3: float
    package_volume_cm3: float
    fill_ratio: float
    surface_area_m2: float
    material_usage_g: float
    estimated_cost: float
    score: float

    model_config = {"from_attributes": True}


class CartonResultSchema(BaseModel):
    length_mm: float
    width_mm: float
    height_mm: float
    units_per_carton: int
    carton_weight_kg: float
    board_grade: str
    carton_material_cost: float

    model_config = {"from_attributes": True}


class PalletResultSchema(BaseModel):
    cartons_per_layer: int
    layers: int
    cartons_per_pallet: int
    pallet_height_mm: float
    total_weight_kg: float

    model_config = {"from_attributes": True}


class ContainerCandidateSchema(BaseModel):
    container_type: str
    pallets_per_container: int
    cartons_per_container: int
    total_units: int
    utilization: float
    empty_space: float
    containers_required: int
    freight_cost: float

    model_config = {"from_attributes": True}


class ContainerResultSchema(BaseModel):
    best: ContainerCandidateSchema
    alternatives: list[ContainerCandidateSchema]

    model_config = {"from_attributes": True}


class ScenarioSchema(BaseModel):
    package: PackageOptionSchema
    carton: CartonResultSchema
    pallet: PalletResultSchema
    container: ContainerResultSchema
    packaging_cost_total: float
    freight_cost_total: float
    total_cost: float

    model_config = {"from_attributes": True}


class ComparisonRowSchema(BaseModel):
    parameter: str
    current: str
    ai: str
    improvement_pct: float | None

    model_config = {"from_attributes": True}


class SimulationResultSchema(BaseModel):
    inputs: SimulationInputSchema
    best_scenario: ScenarioSchema
    alternative_scenarios: list[ScenarioSchema]
    baseline_scenario: ScenarioSchema
    comparison: list[ComparisonRowSchema]
    total_units_required: int

    model_config = {"from_attributes": True}


class CompareResponse(BaseModel):
    inputs: SimulationInputSchema
    comparison: list[ComparisonRowSchema]
    total_savings: float
    savings_pct: float


class SimulationResponse(SimulationResultSchema):
    id: str
    created_at: str


class SimulationListItem(BaseModel):
    id: str
    created_at: str
    tea_density_g_cm3: float
    package_weight_g: float
    shipment_quantity: float
    total_cost_ai: float
    total_savings: float
    savings_pct: float
    container_utilization_ai: float


# --- Granular /optimize/* request schemas -----------------------------------

class PackageOptimizeRequest(BaseModel):
    tea_density_g_cm3: float = Field(..., gt=0)
    package_weight_g: float = Field(..., gt=0)
    package_shape: PackageShape = PackageShape.SQUARE
    packaging_material: PackagingMaterial = PackagingMaterial.PAPER


class PackageOptimizeResponse(BaseModel):
    best: PackageOptionSchema
    alternatives: list[PackageOptionSchema]


class CartonOptimizeRequest(BaseModel):
    package_length_mm: float = Field(..., gt=0)
    package_width_mm: float = Field(..., gt=0)
    package_height_mm: float = Field(..., gt=0)
    package_weight_g: float = Field(..., gt=0)


class PalletOptimizeRequest(BaseModel):
    carton_length_mm: float = Field(..., gt=0)
    carton_width_mm: float = Field(..., gt=0)
    carton_height_mm: float = Field(..., gt=0)
    carton_weight_kg: float = Field(..., gt=0)


class ContainerOptimizeRequest(BaseModel):
    carton_units_per_carton: int = Field(..., gt=0)
    cartons_per_pallet: int = Field(..., gt=0)
    pallet_height_mm: float = Field(..., gt=0)
    pallet_total_weight_kg: float = Field(..., gt=0)
    total_units_required: int = Field(..., gt=0)
