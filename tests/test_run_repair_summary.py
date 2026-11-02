from pathlib import Path
import sys

import pytest

APP_DIR = Path(__file__).resolve().parents[1] / '3DWET' / 'app'
sys.path.insert(0, str(APP_DIR))
import server


RAVN_SUMMARY = """\
 FABM interior state was repaired      250670 times.
 FABM surface state was repaired           0 times.
 FABM bottom state was repaired              0 times.
"""


def test_parse_complete_fabm_repair_summary():
    assert server._parse_fabm_repair_summary(RAVN_SUMMARY) == {
        'interior': 250670, 'surface': 0, 'bottom': 0,
    }


def test_parse_zero_counts():
    log = "\n".join(f'FABM {name} state was repaired 0 times.'
                     for name in ('interior', 'surface', 'bottom'))
    assert server._parse_fabm_repair_summary(log) == {'interior': 0, 'surface': 0, 'bottom': 0}


@pytest.mark.parametrize('log', [
    '',
    'old solver: 250670 interior repairs',
    'FABM interior state was repaired 4 times.\nFABM surface state was repaired 0 times.',
])
def test_missing_old_or_partial_summary_is_not_provided(log):
    assert server._parse_fabm_repair_summary(log) is None


@pytest.fixture
def run_status_client(monkeypatch, tmp_path):
    case_a, case_b = tmp_path / 'case-a', tmp_path / 'case-b'
    case_a.mkdir(); case_b.mkdir()
    monkeypatch.setattr(server, 'run_status', 'completed')
    monkeypatch.setattr(server, 'active_case_path', case_a)
    monkeypatch.setattr(server, 'run_case_path', None)
    monkeypatch.setattr(server, '_run_repair_summary_counts',
                        {'interior': 2, 'surface': 0, 'bottom': 1}, raising=False)
    monkeypatch.setattr(server, '_run_repair_summary_case_path', case_a, raising=False)
    monkeypatch.setattr(server, '_run_repair_summary_status', 'completed', raising=False)
    return server.app.test_client(), case_a, case_b


def test_run_status_only_exposes_completed_summary_for_same_case(run_status_client, monkeypatch):
    client, case_a, case_b = run_status_client
    result = client.get('/api/run/status').get_json()['fabm_repair_summary']
    assert result == {'state': 'available', 'counts': {'interior': 2, 'surface': 0, 'bottom': 1}}

    monkeypatch.setattr(server, 'active_case_path', case_b)
    switched = client.get('/api/run/status').get_json()['fabm_repair_summary']
    assert switched == {'state': 'not_provided', 'counts': None}


def test_running_run_never_exposes_previous_final_counts(run_status_client, monkeypatch):
    client, _case_a, _case_b = run_status_client
    monkeypatch.setattr(server, 'run_status', 'running')
    monkeypatch.setattr(server, 'run_case_path', _case_a)
    result = client.get('/api/run/status').get_json()['fabm_repair_summary']
    assert result == {'state': 'running', 'counts': None}


def test_failed_run_can_expose_only_its_complete_summary(run_status_client, monkeypatch):
    client, _case_a, _case_b = run_status_client
    monkeypatch.setattr(server, 'run_status', 'failed')
    result = client.get('/api/run/status').get_json()['fabm_repair_summary']
    assert result['state'] == 'not_provided', 'summary from a different run status must not be reused'

    monkeypatch.setattr(server, '_run_repair_summary_counts',
                        {'interior': 2, 'surface': 0, 'bottom': 1})
    monkeypatch.setattr(server, '_run_repair_summary_status', 'failed')
    result = client.get('/api/run/status').get_json()['fabm_repair_summary']
    assert result == {'state': 'available', 'counts': {'interior': 2, 'surface': 0, 'bottom': 1}}


def test_capture_ignores_incomplete_runs_and_preexisting_logs(tmp_path, monkeypatch):
    case = tmp_path / 'case'; case.mkdir()
    (case / 'model_run.log').write_text(RAVN_SUMMARY, encoding='utf-8')
    monkeypatch.setattr(server, 'run_case_path', case)
    server._capture_run_repair_summary(case, 'running', True)
    assert server._run_repair_summary_counts is None
    server._capture_run_repair_summary(case, 'completed', False)
    assert server._run_repair_summary_counts is None


def test_capture_requires_current_run_case_path(tmp_path, monkeypatch):
    run_case, other_case = tmp_path / 'run-case', tmp_path / 'other-case'
    run_case.mkdir(); other_case.mkdir()
    (run_case / 'model_run.log').write_text(RAVN_SUMMARY, encoding='utf-8')
    monkeypatch.setattr(server, 'run_case_path', other_case)
    server._capture_run_repair_summary(run_case, 'failed', True)
    assert server._run_repair_summary_counts is None


def test_new_run_reset_clears_a_previous_task_summary():
    server._run_repair_summary_counts = {'interior': 1, 'surface': 0, 'bottom': 0}
    server._run_repair_summary_case_path = Path('old-case')
    server._run_repair_summary_status = 'completed'
    server._reset_run_repair_summary()
    assert server._run_repair_summary_counts is None
    assert server._run_repair_summary_case_path is None
    assert server._run_repair_summary_status is None
