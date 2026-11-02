import hashlib
import json
import sys
from pathlib import Path

APP = Path(__file__).parents[1] / "app"
sys.path.insert(0, str(APP))
import server


def _case(root, name, manifest=True, partial=False):
    path = root / name
    path.mkdir(parents=True)
    (path / "getm.inp").write_text("", encoding="utf-8")
    if manifest:
        from proxy_engineering import REQUIRED_GETM_INPUTS
        sources = []
        for filename in REQUIRED_GETM_INPUTS:
            source = path / filename
            source.write_text("river_method = 0\n" if filename == "getm.inp" else f"fixture {filename}", encoding="utf-8")
            sources.append({"path": filename, "bytes": source.stat().st_size,
                            "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                            "role": "derived", "purpose": "API test fixture"})
        (path / "proxy_engineering.json").write_text(json.dumps({
            "schema_version": 1,
            "kind": "engineering_proxy",
            "target_lake": "Erken",
            "validation_status": "not_scientifically_validated",
            "prepared": True,
            "partial_engineering_proxy": partial,
            "disabled_modules": ["wet/inorganic_carbon", "wet/methane"] if partial else [],
            "geometry": {"status": "derived", "description": "source-derived grid"},
            "forcing": {"status": "synthetic_proxy", "description": "engineering forcing"},
            "sources": sources,
        }), encoding="utf-8")
    return path


def test_case_list_labels_only_cases_with_valid_provenance_manifest(tmp_path, monkeypatch):
    root = tmp_path / "cases"
    root.mkdir()
    _case(root, "Engineering proxy · Erken")
    _case(root, "Engineering proxy · Erken partial", partial=True)
    _case(root, "Erken", manifest=False)
    monkeypatch.setattr(server, "CASE_DIR", root)
    monkeypatch.setattr(server, "LEGACY_CASE_DIR", tmp_path / "legacy")
    monkeypatch.setattr(server, "PROXY_CASE_DIR", tmp_path / "proxy")
    monkeypatch.setattr(server, "_load_external_cases", lambda: [])
    monkeypatch.setattr(server, "find_output_files", lambda _path: {"2d": None, "3d": None})
    monkeypatch.setattr(server, "_is_gotm_result_dir", lambda _path: False)
    monkeypatch.setattr(server, "_is_trusted_gotm_working_copy", lambda _path: False)

    response = server.app.test_client().get("/api/cases")
    cases = {item["name"]: item for item in response.get_json()}

    assert cases["Engineering proxy · Erken"]["engineering_proxy"] is True
    assert cases["Engineering proxy · Erken"]["target_lake"] == "Erken"
    assert cases["Engineering proxy · Erken"]["scientific_validation_status"] == "not_scientifically_validated"
    assert "engineering_proxy" not in cases["Erken"]
    assert cases["Engineering proxy · Erken partial"]["partial_engineering_proxy"] is True


def test_case_list_reports_invalid_manifest_without_inferring_proxy_status(tmp_path, monkeypatch):
    root = tmp_path / "cases"
    root.mkdir()
    path = _case(root, "Erken", manifest=False)
    (path / "proxy_engineering.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(server, "CASE_DIR", root)
    monkeypatch.setattr(server, "LEGACY_CASE_DIR", tmp_path / "legacy")
    monkeypatch.setattr(server, "PROXY_CASE_DIR", tmp_path / "proxy")
    monkeypatch.setattr(server, "_load_external_cases", lambda: [])
    monkeypatch.setattr(server, "find_output_files", lambda _path: {"2d": None, "3d": None})
    monkeypatch.setattr(server, "_is_gotm_result_dir", lambda _path: False)
    monkeypatch.setattr(server, "_is_trusted_gotm_working_copy", lambda _path: False)

    case = server.app.test_client().get("/api/cases").get_json()[0]
    assert "engineering_proxy" not in case
    assert len(case["proxy_manifest_warning"]) <= 240


def test_incomplete_preparation_is_visible_but_not_runnable(tmp_path, monkeypatch):
    root = tmp_path / "cases"
    root.mkdir()
    path = root / "engineering-proxy-Erken"
    path.mkdir()
    (path / "proxy_engineering.json").write_text(json.dumps({
        "schema_version": 1, "kind": "engineering_proxy", "target_lake": "Erken",
        "validation_status": "not_scientifically_validated", "prepared": False,
        "geometry": {"status": "missing", "description": "No 3D grid"},
        "forcing": {"status": "missing", "description": "No spatial forcing"},
        "sources": [{"path": "missing/bathymetry.nc", "role": "missing",
                     "status": "missing", "purpose": "spatial 3D grid"}],
        "blockers": ["Missing spatial 3D grid"],
    }), encoding="utf-8")
    monkeypatch.setattr(server, "CASE_DIR", root)
    monkeypatch.setattr(server, "LEGACY_CASE_DIR", tmp_path / "legacy")
    monkeypatch.setattr(server, "PROXY_CASE_DIR", tmp_path / "proxy")
    monkeypatch.setattr(server, "_load_external_cases", lambda: [])
    monkeypatch.setattr(server, "find_output_files", lambda _path: {"2d": None, "3d": None})
    monkeypatch.setattr(server, "_is_gotm_result_dir", lambda _path: False)
    monkeypatch.setattr(server, "_is_trusted_gotm_working_copy", lambda _path: False)

    cases = server.app.test_client().get("/api/cases").get_json()
    assert len(cases) == 1
    assert cases[0]["engineering_proxy"] is True
    assert cases[0]["prepared"] is False
    assert cases[0]["case_loadable"] is False
    assert cases[0]["proxy_blockers"] == ["Missing spatial 3D grid"]
    response = server.app.test_client().post("/api/case/load", json={
        "case_name": path.name, "case_path": str(path)})
    assert response.status_code == 409
    assert "Missing spatial 3D grid" in response.get_json()["error"]
