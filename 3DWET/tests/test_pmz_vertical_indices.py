from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
ALLOCATIONS = (ROOT / "src/getm/src/3d/dynamic_allocations_3d.h").read_text(
    encoding="utf-8"
).lower()
ADAPTIVE = (ROOT / "src/getm/src/3d/adaptive_coordinates.F90").read_text(
    encoding="utf-8"
).lower()


def test_pmz_bottom_indices_are_initialized_over_the_allocated_domain():
    """Every vertical-coordinate mode needs valid PMZ bounds before use."""
    names = ("kmin_pmz", "kumin_pmz", "kvmin_pmz")
    for name in names:
        match = re.search(
            rf"allocate\(\s*{name}\s*\(\s*i2dfield\s*\)\s*,\s*stat\s*=\s*rc\s*\)(.*?)(?=allocate\s*\(|\Z)",
            ALLOCATIONS,
            re.DOTALL,
        )
        assert match, f"missing I2DFIELD allocation for {name}"
        assert re.search(rf"^\s*{name}\s*=\s*1\s*$", match.group(1), re.MULTILINE), (
            f"{name} must be initialized as a whole array after allocation so all "
            "local and halo cells have a valid bottom index"
        )


def test_adaptive_coordinates_can_recompute_pmz_bottom_indices():
    for name in ("kmin_pmz", "kumin_pmz", "kvmin_pmz"):
        assert re.search(rf"^\s*{name}\s*=\s*1\s*$", ADAPTIVE, re.MULTILINE)
