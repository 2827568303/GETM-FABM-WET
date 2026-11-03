"""Default report paths for the Erken seasonal attempt-03 checkers."""
import argparse
from pathlib import Path

_ATTEMPT = Path(r"D:\GETM-FABM-WET-outputs\build\real-use-validation-20261026\erken-seasonal-attempt03")
DEFAULT_RESULT_REPORT = _ATTEMPT / "result_validation.json"
DEFAULT_NUMERICAL_REPORT = _ATTEMPT / "numerical_health.json"


def add_report_argument(parser: argparse.ArgumentParser, default: Path) -> None:
    parser.add_argument("--report", type=Path, default=default)
