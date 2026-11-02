"""Contract tests for the real-solver calibration acceptance harness."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import verify_calibration_acceptance as acceptance


def test_scipy_simulation_budget_covers_finite_difference_evaluations_and_is_bounded():
    params = [
        {'module': 'diatoms', 'param': 'cMuMax', 'min': 1.2, 'max': 3.6},
        {'module': 'POM', 'param': 'kDMinW', 'min': 0.0005, 'max': 0.0035},
    ]
    budget = acceptance.scipy_simulation_budget(iterations=10, params=params)
    assert budget == 10 * (2 * len(params) + 1) == 50
    assert budget <= acceptance.MAX_SCIPY_SIMULATIONS


def test_scipy_simulation_budget_rejects_invalid_configuration():
    import pytest

    with pytest.raises(ValueError, match='positive'):
        acceptance.scipy_simulation_budget(iterations=0, params=[{'param': 'p'}])
    with pytest.raises(ValueError, match='at least one'):
        acceptance.scipy_simulation_budget(iterations=10, params=[])
