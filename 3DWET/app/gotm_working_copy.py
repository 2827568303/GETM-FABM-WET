"""Trusted, self-contained copies of native single-column GOTM references."""
import hashlib
import hmac
import json
import math
import os
import secrets
import shutil
import time
from datetime import datetime
from pathlib import Path, PurePosixPath

import numpy as np
from netCDF4 import num2date

MANIFEST = ".wet-gotm-working-copy.json"
KIND = "official_gotm_reference_working_copy"
_ALLOWED_SUFFIXES = {".yaml", ".yml", ".dat", ".nc", ".txt"}
_ALLOWED_NAMES = {"gotm_release.exe", "gotm.yaml", "fabm.yaml", "output.yaml",
                  "native_variable_metadata.json", "wet_advanced.txt"}
_MUTABLE_RESULTS = {"output.nc", "restart.nc", "model_run.log", "run.log"}


def _allowed(relative):
    path = PurePosixPath(relative)
    return (not path.is_absolute() and ".." not in path.parts and
            path.name.lower() != "gotm_debug.exe" and
            (path.name.lower() == "gotm_release.exe" or path.suffix.lower() in {".yaml", ".yml", ".dat", ".nc"}
             or path.name.lower() in _ALLOWED_NAMES))


def _inventory(root):
    files = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if rel == MANIFEST:
            continue
        if rel.casefold() in {"input/readme.txt", "output/readme.txt",
                              "analysis/readme.txt", "calibration/readme.txt"}:
            continue
        if path.is_symlink():
            raise ValueError(f"Symbolic links are not allowed: {rel}")
        if path.is_dir():
            continue
        if path.name.lower() in _MUTABLE_RESULTS:
            continue
        if not path.is_file() or not _allowed(rel):
            raise ValueError(f"File is outside the GOTM copy allowlist: {rel}")
        files[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def _payload(files):
    return {"schema": 1, "kind": KIND, "case_type": "gotm_single_column",
            "files": files}


def _signature(payload, key):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hmac.new(key, raw, hashlib.sha256).hexdigest()


def load_or_create_key(path):
    """Keep the trust key outside user case folders."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        key = path.read_bytes()
        if len(key) >= 32:
            return key
    except FileNotFoundError:
        pass
    key = secrets.token_bytes(32)
    try:
        with path.open("xb") as stream:
            stream.write(key)
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass
        return key
    except FileExistsError:
        return path.read_bytes()


def create_working_copy(source, destination, key):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError("Source and destination must be separate directory trees")
    if not source.is_dir() or not (source / "gotm.yaml").is_file() or not (source / "output.nc").is_file():
        raise ValueError("Source is not a GOTM reference with original results")
    if not (source / "gotm_release.exe").is_file():
        raise ValueError("GOTM reference has no gotm_release.exe")
    if (source / "gotm_release.exe").read_bytes()[:2] != b"MZ":
        raise ValueError("gotm_release.exe is not a Windows PE executable")
    if destination.exists() and any(destination.iterdir()):
        raise ValueError("Destination must be empty")
    destination.mkdir(parents=True, exist_ok=True)
    for path in source.rglob("*"):
        rel = path.relative_to(source).as_posix()
        if path.is_symlink():
            raise ValueError(f"Symbolic links are not allowed: {rel}")
        if path.is_dir():
            continue
        if _allowed(rel):
            target = destination / Path(*PurePosixPath(rel).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    files = _inventory(destination)
    payload = _payload(files)
    record = {**payload, "hmac_sha256": _signature(payload, key)}
    (destination / MANIFEST).write_text(json.dumps(record, sort_keys=True, indent=2), encoding="utf-8")
    return record


def validate_working_copy(case, key):
    case = Path(case).resolve()
    try:
        record = json.loads((case / MANIFEST).read_text(encoding="utf-8"))
        payload = {k: record[k] for k in ("schema", "kind", "case_type", "files")}
        if payload["schema"] != 1 or payload["kind"] != KIND or payload["case_type"] != "gotm_single_column":
            return False
        if not hmac.compare_digest(str(record.get("hmac_sha256", "")), _signature(payload, key)):
            return False
        actual = _inventory(case)
        if actual != payload["files"]:
            return False
        exe = case / "gotm_release.exe"
        return ("gotm_release.exe" in actual and "gotm.yaml" in actual
                and exe.read_bytes()[:2] == b"MZ")
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        return False


def validate_gotm_output(case_path, nc_open, *, started_at=None, expected_range=None):
    begin = time.perf_counter()
    report = {"ready": False, "errors": [], "bad_variables": [], "files": [], "time_range": None}
    case = Path(case_path).resolve()
    output = case / "output.nc"
    try:
        if output.is_symlink() or not output.is_file() or output.resolve().parent != case:
            raise ValueError("output.nc must be a regular file inside the GOTM case")
        if started_at is not None and output.stat().st_mtime < float(started_at):
            raise ValueError("output.nc is older than the current run")
        with nc_open(output) as ds:
            tv = ds.variables.get("time")
            if tv is None or tv.ndim != 1 or tv.size < 2 or not np.all(np.isfinite(tv[:])):
                raise ValueError("GOTM output requires at least two finite time records")
            t = np.asarray(tv[:], dtype=float)
            if np.any(np.diff(t) <= 0):
                raise ValueError("GOTM output time must be strictly increasing")
            units = str(getattr(tv, "units", ""))
            if not units:
                raise ValueError("GOTM time coordinate has no units")
            values = num2date([t[0], t[-1]], units,
                              calendar=getattr(tv, "calendar", "standard"),
                              only_use_cftime_datetimes=False)
            time_range = [x.strftime("%Y-%m-%d %H:%M:%S") for x in values]
            if expected_range and (time_range[0] > expected_range[0] or time_range[1] < expected_range[1]):
                raise ValueError("GOTM output does not cover the configured time range")
            fields = 0
            for var in ds.variables.values():
                if "time" not in var.dimensions or var.name == "time":
                    continue
                fields += 1
                dims = tuple(var.dimensions)
                if not dims or dims[0] != "time":
                    raise ValueError(f"{var.name} is not a GOTM time-dependent field")
                if any(dim not in {"time", "z", "zi", "lat", "lon"} for dim in dims):
                    raise ValueError(f"{var.name} has an unsupported spatial dimension")
                if any(var.shape[index] != 1 for index, dim in enumerate(dims)
                       if dim in {"lat", "lon"}):
                    raise ValueError(f"{var.name} has a non-singleton horizontal dimension")
                vertical_dims = [dim for dim in dims if dim in {"z", "zi"}]
                if len(vertical_dims) > 1:
                    raise ValueError(f"{var.name} has multiple vertical dimensions")
                data = np.ma.asarray(var[:])
                if np.any(~np.isfinite(np.asarray(data.data)[~np.ma.getmaskarray(data)])):
                    report["bad_variables"].append(var.name)
            if not fields:
                raise ValueError("GOTM output has no time-dependent model fields")
            for name in ("h", "z"):
                geometry = ds.variables.get(name)
                if geometry is None or geometry.ndim != 4 or geometry.dimensions[:2] != ("time", "z") or geometry.shape[2:] != (1, 1):
                    raise ValueError(f"GOTM output lacks native {name} geometry")
                if not np.all(np.isfinite(np.ma.asarray(geometry[:]).compressed())):
                    raise ValueError(f"GOTM {name} geometry contains nonfinite values")
            report["files"] = [{"file": "output.nc", "records": int(tv.size)}]
            report["time_range"] = time_range
            if report["bad_variables"]:
                raise ValueError("GOTM fields contain nonfinite values")
    except (OSError, RuntimeError, ValueError, TypeError, KeyError, OverflowError) as exc:
        report["errors"].append(str(exc))
    report["ready"] = not report["errors"] and bool(report["files"])
    report["duration_seconds"] = round(time.perf_counter() - begin, 6)
    return report
