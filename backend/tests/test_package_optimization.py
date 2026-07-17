import pytest

from app.optimization.package import optimize_package
from app.optimization.models import PackageShape, PackagingMaterial


def test_product_volume_matches_density_physics():
    best, _ = optimize_package(0.5, 200, PackageShape.SQUARE, PackagingMaterial.PAPER)
    assert best.product_volume_cm3 == pytest.approx(200 / 0.5, rel=1e-6)


def test_fill_ratio_is_bounded_and_reasonable():
    best, candidates = optimize_package(0.45, 250, PackageShape.SQUARE, PackagingMaterial.PAPER)
    for cand in candidates:
        assert 0 < cand.fill_ratio <= 1.0
    # best candidate should be at or above the engine's target fill ratio
    # class (rounding only ever adds a little headspace, never removes it)
    assert best.fill_ratio >= 0.7


def test_round_shape_produces_cylindrical_candidates():
    best, candidates = optimize_package(0.5, 100, PackageShape.ROUND, PackagingMaterial.METAL)
    assert best.shape == PackageShape.ROUND
    assert best.length_mm == best.width_mm  # diameter used for both
    assert len(candidates) == 3


def test_square_shape_produces_three_named_candidates():
    _, candidates = optimize_package(0.5, 100, PackageShape.SQUARE, PackagingMaterial.PLASTIC)
    names = {c.name for c in candidates}
    assert names == {"cube", "standard_pouch", "flat_pack"}


def test_candidates_sorted_best_first_by_score():
    _, candidates = optimize_package(0.4, 500, PackageShape.SQUARE, PackagingMaterial.PAPER)
    scores = [c.score for c in candidates]
    assert scores == sorted(scores, reverse=True)


@pytest.mark.parametrize("bad_density", [0, -1])
def test_rejects_non_positive_density(bad_density):
    with pytest.raises(ValueError):
        optimize_package(bad_density, 100, PackageShape.SQUARE, PackagingMaterial.PAPER)


@pytest.mark.parametrize("bad_weight", [0, -5])
def test_rejects_non_positive_weight(bad_weight):
    with pytest.raises(ValueError):
        optimize_package(0.5, bad_weight, PackageShape.SQUARE, PackagingMaterial.PAPER)
