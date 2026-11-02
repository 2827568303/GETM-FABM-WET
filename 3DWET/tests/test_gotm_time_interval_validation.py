import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parents[1] / "app"))
import server


@pytest.mark.parametrize("time_config", [
    {"start": "not-a-date", "stop": "2000-01-02 00:00:00", "dt": 60},
    {"start": "2000-01-02 00:00:00", "stop": "2000-01-01 00:00:00", "dt": 60},
    {"start": "2000-01-01 00:00:00", "stop": "2000-01-01 00:00:00", "dt": 60},
])
@pytest.mark.parametrize("endpoint", [
    "/api/run/check", "/api/run/estimate", "/api/run/start"])
def test_gotm_rejects_unparseable_or_nonincreasing_time_interval(
        tmp_path, monkeypatch, time_config, endpoint):
    case = tmp_path / "gotm-working-copy"
    case.mkdir()
    (case / "gotm.yaml").write_text(
        yaml.safe_dump({"time": time_config}), encoding="utf-8")
    # A minimal PE signature lets /start reach the time validation on Windows.
    (case / "gotm_release.exe").write_bytes(b"MZ")

    monkeypatch.setattr(server, "active_case_path", case)
    monkeypatch.setattr(server, "_is_trusted_gotm_working_copy", lambda _path: True)
    monkeypatch.setattr(server, "_active_case_is_read_only_gotm", lambda: False)
    monkeypatch.setattr(server, "run_thread", None)
    monkeypatch.setattr(server, "run_status", "idle")
    monkeypatch.setattr(server.threading, "Thread", lambda **_kwargs: type(
        "NoStartThread", (), {"start": lambda _self: None})())

    client = server.app.test_client()
    response = client.post(endpoint) if endpoint.endswith("start") else client.get(endpoint)

    assert response.status_code == (200 if endpoint.endswith("check") else 400)
    if endpoint.endswith("check"):
        payload = response.get_json()
        assert payload["engine"] == "gotm"
        assert payload["model_dimension"] == "single_column"
        assert payload["ok"] is False
        assert payload["blocking"] == 1
        assert payload["checks"][0]["level"] == "error"
    elif endpoint.endswith("estimate"):
        assert "GOTM 时间配置无效" in response.get_json()["error"]
    else:
        assert response.get_json()["success"] is False
        assert "GOTM 时间配置无效" in response.get_json()["error"]

