import argparse
import importlib.util
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
HELPER_PATH = REPO_ROOT / "scripts" / "attempt03_report_paths.py"
SPEC = importlib.util.spec_from_file_location("attempt03_report_paths", HELPER_PATH)
assert SPEC is not None and SPEC.loader is not None
REPORT_PATHS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPORT_PATHS)
DEFAULT_NUMERICAL_REPORT = REPORT_PATHS.DEFAULT_NUMERICAL_REPORT
DEFAULT_RESULT_REPORT = REPORT_PATHS.DEFAULT_RESULT_REPORT
add_report_argument = REPORT_PATHS.add_report_argument


def parse_report(default: Path, argv: list[str]) -> Path:
    parser = argparse.ArgumentParser()
    add_report_argument(parser, default)
    return parser.parse_args(argv).report


class Attempt03ReportPathTests(unittest.TestCase):
    def test_analyzer_defaults_write_to_d_drive(self):
        expected_dir = Path(
            r"D:\GETM-FABM-WET-outputs\build\real-use-validation-20261026\erken-seasonal-attempt03"
        )
        self.assertEqual(DEFAULT_RESULT_REPORT, expected_dir / "result_validation.json")
        self.assertEqual(DEFAULT_NUMERICAL_REPORT, expected_dir / "numerical_health.json")
        self.assertEqual(parse_report(DEFAULT_RESULT_REPORT, []), DEFAULT_RESULT_REPORT)
        self.assertEqual(parse_report(DEFAULT_NUMERICAL_REPORT, []), DEFAULT_NUMERICAL_REPORT)

    def test_explicit_report_destination_overrides_default(self):
        destination = Path("custom") / "report.json"
        self.assertEqual(parse_report(DEFAULT_RESULT_REPORT, ["--report", str(destination)]), destination)
        self.assertEqual(parse_report(DEFAULT_NUMERICAL_REPORT, ["--report", str(destination)]), destination)


if __name__ == "__main__":
    unittest.main()
