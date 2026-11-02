import sys
import tempfile
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "app"))
import server


def test_pytest_temp_case_paths_are_not_persistable(tmp_path):
    pytest_case = Path(tempfile.gettempdir()) / "pytest-of-agent" / "pytest-123" / "test_open0" / "case"
    user_case = Path(tempfile.gettempdir()) / "ordinary-lake-case"

    assert server._is_pytest_temporary_case_path(pytest_case) is True
    assert server._is_pytest_temporary_case_path(user_case) is False


def test_case_persistence_files_use_test_state_directory(tmp_path, monkeypatch):
    monkeypatch.setenv("WET_CASE_STATE_DIR", str(tmp_path / "isolated-state"))
    state_dir = tmp_path / "isolated-state"
    state_dir.mkdir()
    pytest_case = Path(tempfile.gettempdir()) / "pytest-of-agent" / "pytest-123" / "test_restore0" / "case"
    (state_dir / ".active_case.json").write_text(
        json.dumps({"path": str(pytest_case)}), encoding="utf-8")

    import importlib
    fresh_server = importlib.reload(server)

    assert fresh_server._LAST_CASE_FILE.parent == tmp_path / "isolated-state"
    assert fresh_server.EXTERNAL_CASES_FILE.parent == tmp_path / "isolated-state"
    assert fresh_server.active_case_path is None
    assert not fresh_server._LAST_CASE_FILE.exists()


def test_case_open_keeps_pytest_path_out_of_persistent_state(tmp_path):
    case = tmp_path / "case"
    case.mkdir()
    (case / "getm.inp").write_text("", encoding="utf-8")

    response = server.app.test_client().post("/api/case/open", json={"path": str(case)})

    assert response.status_code == 200
    assert not server._LAST_CASE_FILE.exists()
    assert str(case.resolve()) not in server._load_external_cases()


def test_external_registry_still_keeps_legitimate_user_paths():
    user_case = server.CASE_DIR / "Theoretical lake"

    server._register_external_case(user_case)

    assert str(user_case.resolve()) in server._load_external_cases()

