"""
Assumption tables for the optimization engine.

All figures here are *illustrative industry-typical values*, not sourced from a
specific client's real cost/rate card (none was supplied in the brief). They are
intentionally isolated in one module so they can be swapped for real client data
without touching any optimization logic. Every constant is documented with the
reasoning behind its value.

Units used throughout the engine (chosen for packaging-engineering readability):
- length: millimetres (mm)
- weight: grams (g) for package-level figures, kilograms (kg) for carton/pallet/
  container-level figures
- volume: cubic millimetres (mm3) internally, converted to cm3/m3 for display
- cost: USD (arbitrary currency unit - swap CURRENCY if needed)
"""

CURRENCY = "USD"

# ---------------------------------------------------------------------------
# Package (inner pouch / tin) generation
# ---------------------------------------------------------------------------

# Loose tea never packs at 100% density into a container - there has to be
# headspace for sealing, settling, and pour. 0.85 is a common target fill
# ratio used in FMCG pouch design for granular/leaf products.
TARGET_FILL_RATIO = 0.85

# Candidate aspect ratios (L : W : H) tried for square/rectangular pouches.
# "cube" balances material use, "standard" mimics a typical stand-up tea
# pouch, "flat" mimics a flat sachet/box format.
SQUARE_ASPECT_CANDIDATES = {
    "cube": (1.0, 1.0, 1.0),
    "standard_pouch": (1.0, 0.55, 1.8),
    "flat_pack": (1.4, 0.4, 1.0),
}

# Candidate height/diameter ratios tried for round (tin/cylindrical) packages.
ROUND_ASPECT_CANDIDATES = {
    "short_wide": 1.2,
    "medium": 1.8,
    "tall": 2.5,
}

# Round up generated dimensions to the nearest manufacturing increment (mm).
DIMENSION_ROUNDING_MM = 1

# Packaging material sheet properties. cost_per_sqm drives estimated cost,
# thickness/density drive the material-usage (weight) figure.
MATERIAL_PROPERTIES = {
    "paper": {"cost_per_sqm": 0.15, "thickness_mm": 0.30, "density_g_cm3": 0.80},
    "plastic": {"cost_per_sqm": 0.20, "thickness_mm": 0.10, "density_g_cm3": 0.95},
    "metal": {"cost_per_sqm": 0.55, "thickness_mm": 0.15, "density_g_cm3": 2.70},
}

# Standard package weight dropdown options (grams), per the brief's
# "Package Weight: Dropdown" requirement.
PACKAGE_WEIGHT_OPTIONS_G = [50, 100, 125, 250, 500, 1000]

# ---------------------------------------------------------------------------
# Carton (master carton) optimization
# ---------------------------------------------------------------------------

# Manual-handling limits used to bound the carton search space.
MAX_CARTON_DIM_MM = 600
MAX_CARTON_WEIGHT_KG = 20.0

# The grid search sizes a carton from *contents* weight alone (board tare is
# only known after the grid is picked). Reserving this fraction of the limit
# for contents keeps the eventual gross weight (contents + board) safely
# under MAX_CARTON_WEIGHT_KG instead of slightly over it.
CARTON_CONTENTS_WEIGHT_BUDGET_FRACTION = 0.92

# Corrugated flap/wall padding added per axis (two walls) when sizing a
# carton tightly around a grid of packages.
CARTON_WALL_PADDING_MM = 10

# Board grade selected from *contents* weight, and its grammage (kg/m2 of
# board) used to estimate carton tare weight from its exterior surface area.
BOARD_GRADE_RULES = [
    (10.0, "3-ply (Single Wall)", 0.55),
    (20.0, "5-ply (Double Wall)", 0.90),
    (float("inf"), "7-ply (Triple Wall)", 1.30),
]

CARTON_MATERIAL_COST_PER_SQM = 0.9  # corrugated board, USD/m2

# ---------------------------------------------------------------------------
# Pallet optimization
# ---------------------------------------------------------------------------

# ISO standard pallet footprint (mm).
PALLET_LENGTH_MM = 1200
PALLET_WIDTH_MM = 1000
PALLET_BASE_HEIGHT_MM = 150
PALLET_TARE_WEIGHT_KG = 25.0

# Typical safe stack height/weight limits for palletized ocean freight.
MAX_PALLET_HEIGHT_MM = 1700
MAX_PALLET_WEIGHT_KG = 1000.0

# ---------------------------------------------------------------------------
# Container optimization
# ---------------------------------------------------------------------------

# Internal dimensions (mm), max payload (kg), and an illustrative flat
# freight rate (USD/container) for each container type.
CONTAINER_TYPES = {
    "20GP": {"length": 5898, "width": 2352, "height": 2393, "payload_kg": 28200, "freight_cost": 1800},
    "40GP": {"length": 12032, "width": 2352, "height": 2393, "payload_kg": 26500, "freight_cost": 2600},
    "40HC": {"length": 12032, "width": 2352, "height": 2698, "payload_kg": 26300, "freight_cost": 2900},
}

# ---------------------------------------------------------------------------
# "Current" (non-optimized, human-decided) baseline used for comparison
# ---------------------------------------------------------------------------

BASELINE_FILL_RATIO = 0.60  # generic pouch, no dimension optimization
BASELINE_PACKING_EFFICIENCY = 0.70  # cartons picked off-the-shelf, not sized to product

BASELINE_CARTONS_MM = [
    (300, 200, 200),
    (400, 300, 250),
    (500, 400, 300),
    (600, 400, 400),
]

BASELINE_PALLET_LAYERS = 5  # fixed rule of thumb, not height-optimized
BASELINE_CONTAINER_TYPE = "40GP"  # always defaults to the common workhorse container
