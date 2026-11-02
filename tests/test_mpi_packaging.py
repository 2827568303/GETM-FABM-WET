"""Regression checks for the portable Windows MPI payload."""
import importlib.util
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "3DWET/app"))
SPEC = importlib.util.spec_from_file_location("mpi_build_app", ROOT / "scripts/build_app.py")
BUILD_APP = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD_APP)


def test_copy_mpi_payload_stages_solver_mpiexec_runtime_license_and_merger(tmp_path):
    source = tmp_path / "repo"
    model = tmp_path / "stage" / "3DWET"
    source_bin = source / "3DWET/bin"
    source_mpi = source_bin / "mpi"
    source_scripts = source / "3DWET/scripts"
    source_mpi.mkdir(parents=True)
    source_scripts.mkdir(parents=True)
    (source_bin / "getm_cartesian_parallel.exe").write_bytes(b"parallel solver")
    for name in ("mpiexec.exe", "msmpi.dll", "MS-MPI-LICENSE.txt", "libmsmpifec.dll"):
        (source_mpi / name).write_bytes(name.encode())
    (source_scripts / "merge_getm_rank_outputs.py").write_text("# merger", encoding="utf-8")

    BUILD_APP.copy_mpi_payload(source, model)

    assert (model / "bin/getm_cartesian_parallel.exe").read_bytes() == b"parallel solver"
    assert (model / "bin/mpi/mpiexec.exe").read_bytes() == b"mpiexec.exe"
    assert (model / "bin/mpi/msmpi.dll").read_bytes() == b"msmpi.dll"
    assert (model / "bin/mpi/MS-MPI-LICENSE.txt").is_file()
    assert (model / "bin/mpi/libmsmpifec.dll").is_file()
    assert (model / "scripts/merge_getm_rank_outputs.py").read_text(encoding="utf-8") == "# merger"


def test_copy_mpi_payload_fails_closed_when_required_runtime_missing(tmp_path):
    source = tmp_path / "repo"
    model = tmp_path / "stage" / "3DWET"
    (source / "3DWET/bin/mpi").mkdir(parents=True)
    (source / "3DWET/bin/getm_cartesian_parallel.exe").touch()
    (source / "3DWET/scripts").mkdir()
    (source / "3DWET/scripts/merge_getm_rank_outputs.py").touch()

    with pytest.raises(FileNotFoundError, match="MPI package payload is incomplete"):
        BUILD_APP.copy_mpi_payload(source, model)


def test_frozen_build_collects_the_dynamic_mpi_runner_module():
    source = (ROOT / "scripts/build_app.py").read_text(encoding="utf-8")
    assert "'solver_runtime', 'mpi_runner'," in source


def test_installer_preflight_requires_all_mpi_components():
    script = (ROOT / "scripts/build_installer.ps1").read_text(encoding="utf-8")
    for path in (
        "3DWET\\bin\\getm_cartesian_parallel.exe",
        "3DWET\\bin\\mpi\\mpiexec.exe",
        "3DWET\\bin\\mpi\\msmpi.dll",
        "3DWET\\scripts\\merge_getm_rank_outputs.py",
    ):
        assert path in script


def test_frozen_payload_resolves_runtime_and_imports_packaged_merger(tmp_path, monkeypatch):
    from netCDF4 import Dataset
    import mpi_runner
    import sys
    from solver_runtime import inspect_runtime

    install = tmp_path / "3DWETStudio"
    internal = install / "_internal"
    model = install / "3DWET"
    model_bin = model / "bin"
    mpi_dir = model_bin / "mpi"
    scripts = model / "scripts"
    external_case = tmp_path / "isolated-run"
    for directory in (internal, model_bin / "runtime", mpi_dir, scripts, external_case):
        directory.mkdir(parents=True, exist_ok=True)
    solver = model_bin / "getm_cartesian_parallel.exe"
    solver.touch()
    (model_bin / "runtime/libgfortran-5.dll").touch()
    (model_bin / "runtime/libnetcdff-7.dll").touch()
    (mpi_dir / "mpiexec.exe").touch()
    (mpi_dir / "msmpi.dll").touch()
    merger_source = scripts / "merge_getm_rank_outputs.py"
    merger_source.write_text(
        "from pathlib import Path\n"
        "def merge_rank_outputs(shards, reference, destination):\n"
        "    Path(destination).touch()\n"
        "    return Path(destination)\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mpi_runner, "__file__", str(internal / "mpi_runner.py"))
    installation = mpi_runner.discover_mpi_installation()
    assert installation["solver"] == solver.resolve()
    assert inspect_runtime(installation["solver"])["ready"]

    (external_case / "bathymetry.nc").touch()
    with Dataset(external_case / "output.0000.nc", "w") as shard:
        shard.createDimension("time", None)
        time = shard.createVariable("time", "f8", ("time",))
        time[:] = [0.0]
    # Force a real import from the simulated frozen payload, not a sys.modules
    # stub or the source checkout's 3DWET/scripts directory.
    monkeypatch.delitem(sys.modules, "merge_getm_rank_outputs", raising=False)

    merged = mpi_runner.merge_case_rank_outputs(external_case, 1)

    assert [Path(path).name for path in merged] == ["output.nc"]
    assert (external_case / "output.nc").is_file()
    assert Path(sys.modules["merge_getm_rank_outputs"].__file__).resolve() == merger_source.resolve()
