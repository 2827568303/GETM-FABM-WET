import hashlib
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "app"))
import server


ARCHIVE_CASE = Path(os.environ.get(
    "WET_ATTEMPT64_CASE",
    r"D:\GETM-FABM-WET-outputs\build\full-workflow-20261025-attempt64\external\3DWET\case\WorkflowPreprocessProxy64",
))


@pytest.mark.skipif(not ARCHIVE_CASE.is_dir(), reason="attempt64 read-only archive is unavailable")
def test_attempt64_preflight_reports_partial_estimate_and_unknown_total(monkeypatch):
    getm_inp = ARCHIVE_CASE / "getm.inp"
    output_yaml = ARCHIVE_CASE / "output.yaml"
    before = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (getm_inp, output_yaml)
    }

    config = server.parse_getm_inp(getm_inp)
    io_spec = config["io_spec"]
    assert io_spec["save_2d"] is True and io_spec["save_3d"] is True
    assert io_spec["step_2d"] == 12 and io_spec["step_3d"] == 12
    sources = server._parse_output_sources(
        server._parse_output_yaml(output_yaml)["variables_raw"]
    )
    assert len(sources) == 11

    estimate = server._output_size_estimate(ARCHIVE_CASE, sources)
    assert estimate["available"] is True
    assert estimate["complete"] is False
    assert estimate["estimate_scope"] == "output_yaml_configured_fields_only"
    assert estimate["includes_getm_2d3d"] is False
    assert estimate["getm_streams"]["2d"]["enabled"] is True
    assert estimate["getm_streams"]["3d"]["enabled"] is True
    assert estimate["getm_streams"]["2d"]["step"] == 12
    assert estimate["getm_streams"]["3d"]["step"] == 12

    monkeypatch.setattr(server, "active_case_path", ARCHIVE_CASE)
    monkeypatch.setattr(server, "_case_in_use", lambda _path: False)
    monkeypatch.setattr(server, "_cfl_max_timestep", lambda _path: (None, None))
    monkeypatch.setattr(server, "inspect_forcing_coverage", lambda *_args: [])
    monkeypatch.setattr(server, "find_output_files", lambda *_args: {})
    monkeypatch.setattr(server, "_active_case_is_read_only_gotm", lambda: False)
    monkeypatch.setattr(server, "_is_trusted_gotm_working_copy", lambda _path: False)

    response = server.app.test_client().get("/api/run/check")
    assert response.status_code == 200
    checks = response.get_json()["checks"]
    output_check = next(item for item in checks if "输出体积" in item["title"])
    assert output_check["level"] == "warn"
    assert "完整磁盘需求未知" in output_check["detail"]
    assert "2d.nc" in output_check["detail"] and "3d.nc" in output_check["detail"]

    disk_check = next(item for item in checks if "磁盘空间" in item["title"])
    assert disk_check["level"] == "warn"
    assert "不是完整输出量下界" in disk_check["detail"]

    after = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (getm_inp, output_yaml)
    }
    assert after == before
