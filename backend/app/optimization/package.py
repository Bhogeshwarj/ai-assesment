"""
Module 3 - AI Package Recommendation.

Pipeline stage 1-2: Tea Density -> Product Volume -> candidate Package
(inner pouch/tin) Dimensions.

Logic (transparent by design, per the assessment brief):
1. product_volume = package_weight / tea_density                (physics)
2. package_volume = product_volume / TARGET_FILL_RATIO           (headspace allowance)
3. For the requested shape, try a small set of named aspect-ratio candidates
   (see constants.py) and solve for the linear dimensions that hit
   package_volume exactly, then round to a manufacturable increment.
4. Score each candidate by fill ratio first (closer to 1.0 is better - less
   wasted headspace and material), then by estimated cost as a tiebreaker.
"""
import math

from app.optimization import constants as c
from app.optimization.models import PackageOption, PackageShape, PackagingMaterial


def _round_up(value_mm: float) -> float:
    step = c.DIMENSION_ROUNDING_MM
    return math.ceil(value_mm / step) * step


def _material_metrics(surface_area_mm2: float, material: PackagingMaterial) -> tuple[float, float, float]:
    """Returns (surface_area_m2, material_usage_g, estimated_cost)."""
    props = c.MATERIAL_PROPERTIES[material.value if isinstance(material, PackagingMaterial) else material]
    surface_area_m2 = surface_area_mm2 / 1_000_000
    thickness_m = props["thickness_mm"] / 1000
    density_kg_m3 = props["density_g_cm3"] * 1000
    material_usage_g = surface_area_m2 * thickness_m * density_kg_m3 * 1000
    estimated_cost = surface_area_m2 * props["cost_per_sqm"]
    return surface_area_m2, material_usage_g, estimated_cost


def _square_candidate(name: str, ratios: tuple[float, float, float], package_volume_cm3: float,
                       product_volume_cm3: float, material: PackagingMaterial) -> PackageOption:
    rl, rw, rh = ratios
    package_volume_mm3 = package_volume_cm3 * 1000
    # L=rl*x, W=rw*x, H=rh*x  =>  V = rl*rw*rh*x^3
    x = (package_volume_mm3 / (rl * rw * rh)) ** (1 / 3)
    length, width, height = _round_up(rl * x), _round_up(rw * x), _round_up(rh * x)
    actual_volume_mm3 = length * width * height
    actual_volume_cm3 = actual_volume_mm3 / 1000
    fill_ratio = product_volume_cm3 / actual_volume_cm3
    surface_area_mm2 = 2 * (length * width + width * height + length * height)
    surface_area_m2, material_usage_g, estimated_cost = _material_metrics(surface_area_mm2, material)
    return PackageOption(
        name=name, shape=PackageShape.SQUARE,
        length_mm=length, width_mm=width, height_mm=height,
        product_volume_cm3=round(product_volume_cm3, 2),
        package_volume_cm3=round(actual_volume_cm3, 2),
        fill_ratio=round(fill_ratio, 4),
        surface_area_m2=round(surface_area_m2, 5),
        material_usage_g=round(material_usage_g, 3),
        estimated_cost=round(estimated_cost, 4),
    )


def _round_candidate(name: str, h_to_d_ratio: float, package_volume_cm3: float,
                      product_volume_cm3: float, material: PackagingMaterial) -> PackageOption:
    package_volume_mm3 = package_volume_cm3 * 1000
    # V = pi * (d/2)^2 * h,  h = ratio*d  =>  V = pi*ratio*d^3/4
    d = (4 * package_volume_mm3 / (math.pi * h_to_d_ratio)) ** (1 / 3)
    diameter = _round_up(d)
    height = _round_up(h_to_d_ratio * d)
    radius = diameter / 2
    actual_volume_mm3 = math.pi * radius * radius * height
    actual_volume_cm3 = actual_volume_mm3 / 1000
    fill_ratio = product_volume_cm3 / actual_volume_cm3
    surface_area_mm2 = 2 * math.pi * radius * radius + 2 * math.pi * radius * height
    surface_area_m2, material_usage_g, estimated_cost = _material_metrics(surface_area_mm2, material)
    return PackageOption(
        name=name, shape=PackageShape.ROUND,
        length_mm=diameter, width_mm=diameter, height_mm=height,
        product_volume_cm3=round(product_volume_cm3, 2),
        package_volume_cm3=round(actual_volume_cm3, 2),
        fill_ratio=round(fill_ratio, 4),
        surface_area_m2=round(surface_area_m2, 5),
        material_usage_g=round(material_usage_g, 3),
        estimated_cost=round(estimated_cost, 4),
    )


def optimize_package(
    tea_density_g_cm3: float,
    package_weight_g: float,
    shape: PackageShape,
    material: PackagingMaterial,
) -> tuple[PackageOption, list[PackageOption]]:
    """Returns (best_package, all_candidates_sorted_desc_by_score)."""
    if tea_density_g_cm3 <= 0:
        raise ValueError("tea_density_g_cm3 must be > 0")
    if package_weight_g <= 0:
        raise ValueError("package_weight_g must be > 0")

    product_volume_cm3 = package_weight_g / tea_density_g_cm3
    package_volume_cm3 = product_volume_cm3 / c.TARGET_FILL_RATIO

    candidates: list[PackageOption] = []
    if shape == PackageShape.SQUARE:
        for name, ratios in c.SQUARE_ASPECT_CANDIDATES.items():
            candidates.append(_square_candidate(name, ratios, package_volume_cm3, product_volume_cm3, material))
    else:
        for name, ratio in c.ROUND_ASPECT_CANDIDATES.items():
            candidates.append(_round_candidate(name, ratio, package_volume_cm3, product_volume_cm3, material))

    # Score: fill ratio dominates (rounded to 2 decimals so near-ties don't
    # matter), estimated cost breaks ties. Both are explicit and inspectable.
    for cand in candidates:
        cand.score = round(cand.fill_ratio, 2) - (cand.estimated_cost * 0.001)
    candidates.sort(key=lambda p: p.score, reverse=True)

    return candidates[0], candidates
