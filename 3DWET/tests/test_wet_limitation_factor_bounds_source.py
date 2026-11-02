"""Source contract checks for bounded WET Droop limitation factors."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]


class WetLimitationFactorBoundsTest(unittest.TestCase):
    def assert_assignment_is_clamped(self, source: Path, variable: str) -> None:
        # These legacy Fortran files contain mixed-era Windows encodings; the
        # contract under test is ASCII, so a one-byte decode is sufficient.
        text = source.read_text(encoding="latin-1")
        code = "\n".join(line.split("!", 1)[0] for line in text.splitlines())
        code = re.sub(r"&\s*\n\s*", "", code)
        match = re.search(
            rf"(?im)^\s*{re.escape(variable)}\s*=\s*([^\n]+)", code
        )
        self.assertIsNotNone(match, f"assignment for {variable} not found in {source}")
        rhs = re.sub(r"\s+", "", match.group(1)).lower()
        self.assertRegex(
            rhs,
            r"^min\(1\.0_rk,max\(0\.0_rk,.*\)\)$",
            f"{variable} must be clamped to [0,1], got: {match.group(1)}",
        )

    def test_phytoplankton_droop_factors_are_bounded(self) -> None:
        source = ROOT / "3DWET/src/wet/src/phytoplankton.F90"
        for variable in ("aPLim", "aNLim"):
            with self.subTest(variable=variable):
                self.assert_assignment_is_clamped(source, variable)

    def test_macrophyte_droop_factors_are_bounded(self) -> None:
        source = ROOT / "3DWET/src/wet/src/macrophytes.F90"
        for variable in ("aPLimVeg", "aNLimVeg"):
            with self.subTest(variable=variable):
                self.assert_assignment_is_clamped(source, variable)


if __name__ == "__main__":
    unittest.main()
