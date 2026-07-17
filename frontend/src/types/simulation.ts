export type PackageShape = "square" | "round";
export type PackagingMaterial = "paper" | "plastic" | "metal";
export type ShipmentType = "total_weight" | "per_container";

export interface SimulationInput {
  tea_density_g_cm3: number;
  package_weight_g: number;
  shipment_quantity: number;
  shipment_type: ShipmentType;
  package_shape: PackageShape;
  packaging_material: PackagingMaterial;
  target_market?: string | null;
}

export interface PackageOption {
  name: string;
  shape: PackageShape;
  length_mm: number;
  width_mm: number;
  height_mm: number;
  product_volume_cm3: number;
  package_volume_cm3: number;
  fill_ratio: number;
  surface_area_m2: number;
  material_usage_g: number;
  estimated_cost: number;
  score: number;
}

export interface CartonResult {
  length_mm: number;
  width_mm: number;
  height_mm: number;
  units_per_carton: number;
  carton_weight_kg: number;
  board_grade: string;
  carton_material_cost: number;
}

export interface PalletResult {
  cartons_per_layer: number;
  layers: number;
  cartons_per_pallet: number;
  pallet_height_mm: number;
  total_weight_kg: number;
}

export interface ContainerCandidate {
  container_type: string;
  pallets_per_container: number;
  cartons_per_container: number;
  total_units: number;
  utilization: number;
  empty_space: number;
  containers_required: number;
  freight_cost: number;
}

export interface ContainerResult {
  best: ContainerCandidate;
  alternatives: ContainerCandidate[];
}

export interface Scenario {
  package: PackageOption;
  carton: CartonResult;
  pallet: PalletResult;
  container: ContainerResult;
  packaging_cost_total: number;
  freight_cost_total: number;
  total_cost: number;
}

export interface ComparisonRow {
  parameter: string;
  current: string;
  ai: string;
  improvement_pct: number | null;
}

export interface SimulationResponse {
  id: string;
  created_at: string;
  inputs: SimulationInput;
  best_scenario: Scenario;
  alternative_scenarios: Scenario[];
  baseline_scenario: Scenario;
  comparison: ComparisonRow[];
  total_units_required: number;
}

export interface SimulationListItem {
  id: string;
  created_at: string;
  tea_density_g_cm3: number;
  package_weight_g: number;
  shipment_quantity: number;
  total_cost_ai: number;
  total_savings: number;
  savings_pct: number;
  container_utilization_ai: number;
}

export interface DashboardSummary {
  total_simulations: number;
  total_savings: number;
  average_container_utilization: number;
  recent_simulations: SimulationListItem[];
}
