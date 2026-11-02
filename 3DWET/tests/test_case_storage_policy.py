import os
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "app"))
import case_storage


def test_c_drive_case_override_is_rejected_for_non_c_preferred_root(tmp_path, monkeypatch):
    preferred = tmp_path / "preferred-cases"
    monkeypatch.setattr(case_storage, "PREFERRED_CASE_ROOT", preferred)

    root, source, warning = case_storage.resolve_case_storage(
        tmp_path / "model", {"WET_CASE_DIR": r"C:\legacy\cases"})

    assert root == preferred.resolve()
    assert source == "preferred"
    assert "C: storage is disabled" in warning
    assert not case_storage.is_system_drive(root)


def test_case_storage_fails_closed_when_all_non_c_candidates_are_unwritable(monkeypatch):
    monkeypatch.setattr(case_storage, "PREFERRED_CASE_ROOT", Path(r"C:\should-not-be-used"))

    def deny_write(_path):
        raise PermissionError("read only for test")

    monkeypatch.setattr(case_storage, "_probe_writable", deny_write)
    with pytest.raises(OSError, match="No writable non-C: case storage"):
        case_storage.resolve_case_storage(Path(r"C:\model"), {"WET_CASE_DIR": r"C:\cases"})


def test_c_drive_state_override_uses_non_c_case_state_root(tmp_path):
    case_root = tmp_path / "cases"

    state_root, warning = case_storage.resolve_state_storage(
        case_root, {"WET_CASE_STATE_DIR": r"C:\legacy\state"})

    assert state_root == (case_root / ".state").resolve()
    assert "C: state storage is disabled" in warning
    assert not case_storage.is_system_drive(state_root)


@pytest.mark.parametrize("route", [
    "/api/run/start",
    "/api/case/build",
    "/api/calibration/auto/start",
    "/api/calibration/points/save",
    "/api/case/delete",
])
def test_c_drive_getm_and_external_case_writes_are_blocked(route):
    assert not case_storage.case_request_is_read_only_allowed(
        r"C:\external\lake", "POST", route)


@pytest.mark.parametrize("route", [
    "/api/case/open",
    "/api/case/load",
    "/api/case/save_as",
    "/api/calibration/observations/compare-column",
])
def test_c_drive_cases_keep_safe_open_and_copy_operations(route):
    assert case_storage.case_request_is_read_only_allowed(
        r"C:\legacy\lake", "POST", route)


def test_reads_are_allowed_and_non_c_case_writes_remain_available():
    assert case_storage.case_request_is_read_only_allowed(
        r"C:\legacy\lake", "GET", "/api/run/status")
    assert case_storage.case_request_is_read_only_allowed(
        r"D:\GETM-FABM-WET-outputs\cases\lake", "POST", "/api/run/start")
    assert case_storage.is_system_drive(r"C:\legacy\lake")
    assert not case_storage.is_system_drive(r"D:\GETM-FABM-WET-outputs\cases\lake")


def test_non_windows_ignores_drive_letters_and_uses_the_repository_case_tree(tmp_path, monkeypatch):
    if os.name == "nt":
        pytest.skip("Windows selects a real non-C: volume when one is present")
    monkeypatch.chdir(tmp_path)
    root, source, warning = case_storage.resolve_case_storage(tmp_path / "model", {})
    assert source == "repository"
    assert root == (tmp_path / "model" / "case").resolve()
    assert not (tmp_path / "D:\\GETM-FABM-WET-outputs\\cases").exists()
    assert warning and "Windows drive paths are not used" in warning


def test_installer_without_extra_volume_keeps_cases_outside_the_program(tmp_path, monkeypatch):
    monkeypatch.setattr(case_storage, "PREFERRED_CASE_ROOT", Path(r"D:\GETM-FABM-WET-outputs\cases"))
    local = tmp_path / "Local"
    monkeypatch.setenv("LOCALAPPDATA", str(local))
    program = tmp_path / "Programs" / "3DWET" / "3DWET"
    (program / "case").mkdir(parents=True)
    env = {"LOCALAPPDATA": str(local), "WET_USER_CASES": "1"}

    root, source, warning = case_storage.resolve_case_storage(program, env)

    assert source == "per-user"
    assert root == (local / "3DWET" / "cases").resolve()
    assert program.resolve() not in root.parents
    assert "outside the install directory" in warning
    state, _state_warning = case_storage.resolve_state_storage(root, env)
    assert state == (root / ".state").resolve()
    lake = root / "NativeTest"
    assert case_storage.case_request_is_read_only_allowed(lake, "POST", "/api/run/start")
    assert not case_storage.case_request_is_read_only_allowed(
        r"C:\external\lake", "POST", "/api/run/start")


def test_designated_per_user_folder_on_c_can_run_and_other_c_paths_stay_read_only(monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", r"C:\Users\me\AppData\Local")
    lake = r"C:\Users\me\AppData\Local\3DWET\cases\NativeTest"
    assert case_storage.case_request_is_read_only_allowed(lake, "POST", "/api/run/start")
    assert not case_storage.case_request_is_read_only_allowed(
        r"C:\Users\me\Documents\lake", "POST", "/api/run/start")


def test_save_as_destination_guard_distinguishes_c_and_d():
    assert case_storage.is_system_drive(r"C:\legacy\copy")
    assert not case_storage.is_system_drive(r"D:\GETM-FABM-WET-outputs\cases\copy")

