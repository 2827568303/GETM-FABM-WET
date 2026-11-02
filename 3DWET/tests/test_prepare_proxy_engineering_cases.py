import hashlib
import importlib.util
import sys
from pathlib import Path

import pytest

APP = Path(__file__).parents[1] / "app"
SCRIPT = Path(__file__).parents[1] / "scripts" / "prepare_proxy_engineering_cases.py"
sys.path.insert(0, str(APP))
import proxy_engineering

spec = importlib.util.spec_from_file_location("prepare_proxy_engineering_cases", SCRIPT)
prepare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prepare)


def test_preparation_copies_only_traceable_sources_and_marks_blockers(tmp_path):
    repo_root = Path(__file__).parents[2]
    output = tmp_path / "attempt"
    sources_before = {
        path: hashlib.sha256(path.read_bytes()).hexdigest()
        for lake in ("lake_bryrup_denmark", "lake_arreskov_denmark")
        for path in (repo_root / "3DWET" / "src" / "wet" / "testcases" / lake).glob("*")
        if path.is_file() and path.name != ".gitkeep"
    }

    result = prepare.prepare_proxy_attempt(repo_root, output)

    assert set(result) == {"Erken", "Lake Ravn", "Bryrup", "Arreskov"}
    for lake, record in result.items():
        manifest_path = Path(record["case_path"]) / "proxy_engineering.json"
        manifest = __import__("json").loads(manifest_path.read_text(encoding="utf-8"))
        assert manifest["target_lake"] == lake
        assert manifest["validation_status"] == "not_scientifically_validated"
        assert manifest["prepared"] is (lake == "Erken")
        assert manifest["blockers"] == ([] if lake == "Erken" else manifest["blockers"])
        assert proxy_engineering.validate_manifest(manifest, manifest_path.parent).valid
        assert all(item["role"] == "missing" or item["sha256"] for item in manifest["sources"])
    assert result["Bryrup"]["copied_source_count"] > 0
    assert result["Arreskov"]["copied_source_count"] > 0
    assert result["Erken"]["copied_source_count"] > 0
    assert result["Lake Ravn"]["copied_source_count"] > 0
    assert result["Lake Ravn"]["prepared"] is False
    ravn = __import__("json").loads((Path(result["Lake Ravn"]["case_path"]) / "proxy_engineering.json").read_text(encoding="utf-8"))
    archive = next(source for source in ravn["sources"] if source["path"].endswith(".zip"))
    assert archive["role"] == "upstream_reference"

    for path, digest in sources_before.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest


def test_preparation_refuses_to_overwrite_existing_attempt(tmp_path):
    repo_root = Path(__file__).parents[2]
    output = tmp_path / "attempt"
    output.mkdir()
    sentinel = output / "keep.txt"
    sentinel.write_text("retain", encoding="utf-8")
    with pytest.raises(FileExistsError):
        prepare.prepare_proxy_attempt(repo_root, output)
    assert sentinel.read_text(encoding="utf-8") == "retain"
    assert sorted(path.name for path in output.iterdir()) == ["keep.txt"]


def test_erken_copy_is_independent_and_excludes_historical_outputs(tmp_path):
    repo_root = Path(__file__).parents[2]
    output = tmp_path / "attempt"
    result = prepare.prepare_proxy_attempt(repo_root, output)
    case = Path(result["Erken"]["case_path"])
    source_root = repo_root / prepare.ERKEN_SOURCE
    for name in prepare.ERKEN_FILES:
        source = source_root / name
        if source.is_file():
            assert hashlib.sha256((case / name).read_bytes()).digest() == hashlib.sha256(source.read_bytes()).digest()
    assert not (case / "model_run.log").exists()
    assert not (case / "output").exists()
    manifest = __import__("json").loads((case / "proxy_engineering.json").read_text(encoding="utf-8"))
    assert manifest["prepared"] is True
    assert all(item["role"] == "derived" for item in manifest["sources"])


def test_active_erken_case_is_copied_to_new_storage_path(tmp_path):
    repo_root = Path(__file__).parents[2]
    output = tmp_path / "attempt"
    active = tmp_path / "cases" / "Engineering Proxy - Erken"
    active.parent.mkdir()
    result = prepare.prepare_proxy_attempt(repo_root, output, active)
    assert result["Erken"]["active_case_path"] == str(active.resolve())
    manifest = __import__("json").loads((active / "proxy_engineering.json").read_text(encoding="utf-8"))
    assert manifest["active_case_path"] == str(active.resolve())
    assert proxy_engineering.validate_manifest(manifest, active).valid
    assert manifest["prepared"] is True
    assert "metforcing = .true." in (active / "getm.inp").read_text(encoding="utf-8").lower()
    assert (active / "meteo_input.txt").read_text(encoding="utf-8").strip() == "meteo.nc"
    assert manifest["forcing"]["confirmed"] is False
    assert manifest["engineering_adjustments"][0]["forcing_confirmed"] is False
    source_config = (repo_root / prepare.ERKEN_SOURCE / "getm.inp").read_text(encoding="utf-8").lower()
    assert "metforcing = .false." in source_config
    assert "metforcing = .true." in (active / "getm.inp").read_text(encoding="utf-8").lower()
    assert not (active / "model_run.log").exists()
    assert not (active / "output").exists()
    with pytest.raises(FileExistsError):
        prepare.prepare_proxy_attempt(repo_root, tmp_path / "attempt2", active)


def test_partial_ghg_off_case_removes_only_ghg_instances_and_keeps_provenance(tmp_path):
    repo_root = Path(__file__).parents[2]
    attempt = tmp_path / "attempt"
    active = tmp_path / "cases" / "Erken active"
    active.parent.mkdir()
    prepare.prepare_proxy_attempt(repo_root, attempt, active)
    target = tmp_path / "cases" / "Erken partial proxy"
    source_fabm = __import__("yaml").safe_load((active / "fabm.yaml").read_text(encoding="utf-8"))
    expected_instances = {name: value for name, value in source_fabm["instances"].items()
                          if name not in {"inorganic_carbon", "methane"}}
    source_config_hash = hashlib.sha256((active / "fabm.yaml").read_bytes()).hexdigest()

    manifest = prepare.create_partial_ghg_off_proxy(active, target)

    assert manifest["prepared"] is True
    assert manifest["partial_engineering_proxy"] is True
    assert manifest["disabled_modules"] == ["wet/inorganic_carbon", "wet/methane"]
    assert manifest["active_case_path"] == str(target.resolve())
    partial_yaml = __import__("yaml").safe_load((target / "fabm.yaml").read_text(encoding="utf-8"))
    assert partial_yaml["instances"] == expected_instances
    assert "inorganic_carbon" in source_fabm["instances"] and "methane" in source_fabm["instances"]
    assert hashlib.sha256((active / "fabm.yaml").read_bytes()).hexdigest() == source_config_hash
    assert manifest["forcing"]["confirmed"] is False
    assert proxy_engineering.validate_manifest(manifest, target).valid
    for original in manifest["sources"]:
        if original["path"] == "fabm.yaml":
            assert original["origin_sha256"] == source_config_hash
            assert original["sha256"] != source_config_hash
        else:
            assert hashlib.sha256((target / original["path"]).read_bytes()).hexdigest() == original["sha256"]
    assert not list(target.rglob("model_run.log"))
    assert not list(target.rglob("output.nc"))


def test_missing_source_paths_are_retained_as_explicit_blockers(tmp_path):
    repo_root = tmp_path / "empty-workspace"
    (repo_root / "3DWET" / "src" / "wet" / "testcases").mkdir(parents=True)
    output = tmp_path / "attempt"
    result = prepare.prepare_proxy_attempt(repo_root, output)
    for lake, record in result.items():
        manifest_path = Path(record["case_path"]) / "proxy_engineering.json"
        manifest = __import__("json").loads(manifest_path.read_text(encoding="utf-8"))
        assert not manifest["prepared"]
        assert any(source["role"] == "missing" for source in manifest["sources"])
        assert any(source["role"] == "missing" for source in manifest["sources"])
        assert proxy_engineering.validate_manifest(manifest, manifest_path.parent).valid
