import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "app"))
import server


def _fabm_text():
    return """instances:
  cyanobacteria:
    model: wet/phytoplankton
  burial:
    model: wet/burial
    coupling:
      POM_phytoplankton_update1: cyanobacteria/tDPOMS
"""


def test_disabling_referenced_module_is_refused_without_mutating_config(tmp_path):
    fabm = tmp_path / "fabm.yaml"
    original = _fabm_text().encode("utf-8")
    fabm.write_bytes(original)

    success, blockers = server.toggle_fabm_module(fabm, "cyanobacteria", False)

    assert success is False
    assert blockers == ["burial 通过耦合 POM_phytoplankton_update1 引用 cyanobacteria"]
    assert fabm.read_bytes() == original
    assert not (tmp_path / server.FABM_DISABLED_SIDECAR).exists()


def test_blocked_disable_does_not_migrate_legacy_disabled_block(tmp_path):
    fabm = tmp_path / "fabm.yaml"
    original = """_disabled:
  old_module:
    model: wet/om_pool
instances:
  cyanobacteria:
    model: wet/phytoplankton
  burial:
    model: wet/burial
    coupling:
      POM_phytoplankton_update1: cyanobacteria/tDPOMS
""".encode("utf-8")
    fabm.write_bytes(original)

    success, _ = server.toggle_fabm_module(fabm, "cyanobacteria", False)

    assert success is False
    assert fabm.read_bytes() == original
    assert not (tmp_path / server.FABM_DISABLED_SIDECAR).exists()


def test_force_does_not_bypass_reference_safety_or_mutate_config(tmp_path, monkeypatch):
    fabm = tmp_path / "fabm.yaml"
    original = _fabm_text().encode("utf-8")
    fabm.write_bytes(original)
    monkeypatch.setattr(server, "active_case_path", tmp_path)

    response = server.app.test_client().post(
        "/api/config/fabm/module",
        json={"module": "cyanobacteria", "enabled": False, "force": True},
    )

    assert response.status_code == 409
    payload = response.get_json()
    assert payload["blocked_by_couplings"] is True
    assert any(
        "POM_phytoplankton_update1" in warning and "cyanobacteria" in warning
        for warning in payload["warnings"]
    )
    assert "先在生态网络" in payload["repair_message"]
    assert fabm.read_bytes() == original
    assert not (tmp_path / server.FABM_DISABLED_SIDECAR).exists()
