import hashlib
import json
import sys
from pathlib import Path

import pytest

APP = Path(__file__).parents[1] / "app"
sys.path.insert(0, str(APP))
import proxy_engineering


def _manifest(tmp_path):
    runtime_files = sorted(proxy_engineering.REQUIRED_GETM_INPUTS)
    for filename in runtime_files:
        content = b"river_method = 0\n" if filename == "getm.inp" else (filename + " fixture").encode()
        (tmp_path / filename).write_bytes(content)
    source = tmp_path / "source.dat"
    source.write_bytes(b"source bytes")
    sources = [{"path": path.name, "bytes": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "role": "derived", "purpose": "runtime input fixture"}
               for path in (tmp_path / name for name in runtime_files)]
    return {
        "schema_version": 1,
        "kind": "engineering_proxy",
        "target_lake": "Erken",
        "validation_status": "not_scientifically_validated",
        "prepared": True,
        "geometry": {"status": "proxy", "description": "derived grid"},
        "forcing": {"status": "proxy", "description": "spatial broadcast"},
        "sources": sources + [{
            "path": "source.dat", "bytes": source.stat().st_size,
            "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "role": "derived", "purpose": "engineering forcing input"}],
    }


def test_valid_manifest_is_accepted_and_normalized(tmp_path):
    value = _manifest(tmp_path)
    result = proxy_engineering.validate_manifest(value, tmp_path)
    assert result.valid
    assert result.target_lake == "Erken"
    assert result.warning is None


@pytest.mark.parametrize("status", ["validated", "measured", "", None])
def test_unknown_or_scientific_validation_status_is_rejected(tmp_path, status):
    value = _manifest(tmp_path)
    value["validation_status"] = status
    assert not proxy_engineering.validate_manifest(value, tmp_path).valid


def test_present_source_requires_matching_digest_and_byte_count(tmp_path):
    value = _manifest(tmp_path)
    value["sources"][0]["sha256"] = "0" * 64
    assert not proxy_engineering.validate_manifest(value, tmp_path).valid


def test_invalid_source_role_is_rejected(tmp_path):
    value = _manifest(tmp_path)
    value["sources"][0]["role"] = "measured-ish"
    assert not proxy_engineering.validate_manifest(value, tmp_path).valid


def test_missing_input_must_be_explicit_and_cannot_claim_measured(tmp_path):
    value = _manifest(tmp_path)
    value["prepared"] = False
    value["blockers"] = ["Required spatial grid is not present"]
    value["sources"] = [{"path": "Input/missing.nc", "role": "missing",
                         "purpose": "required spatial grid", "status": "missing"}]
    assert proxy_engineering.validate_manifest(value, tmp_path).valid
    value["sources"][0]["role"] = "measured"
    assert not proxy_engineering.validate_manifest(value, tmp_path).valid


def test_manifest_requires_geometry_forcing_and_sources(tmp_path):
    value = _manifest(tmp_path)
    value.pop("forcing")
    assert not proxy_engineering.validate_manifest(value, tmp_path).valid


def test_source_path_cannot_escape_case_root(tmp_path):
    value = _manifest(tmp_path)
    value["sources"][0]["path"] = "../source.dat"
    assert not proxy_engineering.validate_manifest(value, tmp_path).valid


def test_prepared_case_cannot_claim_missing_required_source(tmp_path):
    value = _manifest(tmp_path)
    value["sources"].append({"path": "missing/rivers.nc", "role": "missing",
                             "purpose": "3D river forcing", "status": "missing"})
    assert not proxy_engineering.validate_manifest(value, tmp_path).valid


def test_unprepared_case_requires_specific_blockers(tmp_path):
    value = _manifest(tmp_path)
    value["prepared"] = False
    assert not proxy_engineering.validate_manifest(value, tmp_path).valid
    value["blockers"] = ["Missing spatial grid and bathymetry"]
    assert proxy_engineering.validate_manifest(value, tmp_path).valid


def test_prepared_case_cannot_have_blockers_or_missing_geometry_forcing(tmp_path):
    value = _manifest(tmp_path)
    value["blockers"] = ["missing map"]
    assert not proxy_engineering.validate_manifest(value, tmp_path).valid
    value = _manifest(tmp_path)
    value["geometry"]["status"] = "missing"
    assert not proxy_engineering.validate_manifest(value, tmp_path).valid


def test_prepared_case_requires_every_runtime_input_in_manifest(tmp_path):
    value = _manifest(tmp_path)
    value["sources"] = [source for source in value["sources"] if source["path"] != "getm_fabm.inp"]
    assert not proxy_engineering.validate_manifest(value, tmp_path).valid


def test_upstream_reference_role_is_accepted(tmp_path):
    value = _manifest(tmp_path)
    value["prepared"] = False
    value["blockers"] = ["No spatial grid"]
    value["sources"][-1]["role"] = "upstream_reference"
    assert proxy_engineering.validate_manifest(value, tmp_path).valid


def test_missing_river_files_require_river_method_zero(tmp_path):
    value = _manifest(tmp_path)
    (tmp_path / "getm.inp").write_text("river_method = 1\n", encoding="utf-8")
    value["sources"] = [s for s in value["sources"] if s["path"] not in {"riverinfo.dat", "rivers.nc"}]
    assert not proxy_engineering.validate_manifest(value, tmp_path).valid
    (tmp_path / "getm.inp").write_text("river_method = 0\n", encoding="utf-8")
    for source in value["sources"]:
        if source["path"] == "getm.inp":
            source["bytes"] = (tmp_path / "getm.inp").stat().st_size
            source["sha256"] = hashlib.sha256((tmp_path / "getm.inp").read_bytes()).hexdigest()
    assert proxy_engineering.validate_manifest(value, tmp_path).valid


def test_manifest_rejects_symlink_escape_when_supported(tmp_path):
    outside = tmp_path.parent / f"{tmp_path.name}-outside.txt"
    outside.write_text("outside", encoding="utf-8")
    link = tmp_path / "outside-link.txt"
    try:
        link.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation is unavailable")
    value = _manifest(tmp_path)
    value["sources"][0]["path"] = link.name
    value["sources"][0]["bytes"] = outside.stat().st_size
    value["sources"][0]["sha256"] = hashlib.sha256(outside.read_bytes()).hexdigest()
    assert not proxy_engineering.validate_manifest(value, tmp_path).valid
