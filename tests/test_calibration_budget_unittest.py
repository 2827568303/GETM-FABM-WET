"""Small standard-library checks for explicit calibration cost caps."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET' / 'app'))
import calibration


class CalibrationBudgetTests(unittest.TestCase):
    def test_scipy_stops_at_the_explicit_model_evaluation_cap(self):
        calls = []
        params = [dict(module='m', param=f'p{i}', min=-2, max=2) for i in range(4)]

        def objective(values):
            calls.append(values)
            return sum((item['value'] - 0.25) ** 2 for item in values)

        result = calibration.ScipyEngine().calibrate(
            params, objective, max_iter=100, max_simulations=3)

        self.assertEqual(len(calls), 3)
        self.assertEqual(result['n_iterations'], 3)
        self.assertEqual(result['max_evaluations'], 3)
        self.assertTrue(result['budget_exhausted'])
        self.assertFalse(result['converged'])
        self.assertEqual(len(result['history']), 3)
        self.assertTrue(result['success'], result)

    def test_observation_preflight_requires_variable_and_mapped_point(self):
        points = [dict(id='model-station', point_id='observed-station', variables=['temp'])]
        weights = []
        with self.assertRaisesRegex(ValueError, 'model-station/temp'):
            calibration.validate_calibration_observations(
                points, {}, {'records': [dict(point_id='wrong-station', variable='temp', value=12)]},
                weights, 'rmse')

    def test_observation_preflight_accepts_legacy_data_for_selected_variable(self):
        points = [dict(id='station', variables=['temp'])]
        calibration.validate_calibration_observations(
            points, {'station': {'temp': [dict(value=11.5)]}}, {'records': []}, [], 'rmse')


if __name__ == '__main__':
    unittest.main()
