"""Resolve writable storage for newly created model cases and app scratch data."""
from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path


PREFERRED_CASE_ROOT = Path(r"D:\GETM-FABM-WET-outputs\cases")
_READ_ONLY_CASE_POSTS = {
    ("POST", "/api/case/open"),
    ("POST", "/api/case/load"),
    ("POST", "/api/case/save_as"),
    ("POST", "/api/preprocess/case/create"),
    ("POST", "/api/preprocess/save"),
    ("POST", "/api/system/explore"),
    ("POST", "/api/calibration/observations/compare-column"),
}


def _drive_letter(path: str | Path) -> str | None:
    """Return ``C`` for ``C:\\...`` before pathlib can treat the string as relative.

    On Linux, ``Path('C:/lake').drive`` is empty and ``resolve()`` does not
    raise, so a raw drive letter has to be read from the text itself.
    """
    text = os.fspath(path).replace("/", "\\")
    match = re.match(r"^([A-Za-z]):(?:\\|$)", text)
    if match:
        return match.group(1).upper()
    try:
        drive = Path(path).resolve().drive
    except (OSError, RuntimeError, ValueError):
        return None
    if len(drive) >= 2 and drive[1] == ":":
        return drive[0].upper()
    return None


def is_system_drive(path: str | Path) -> bool:
    """Return whether a Windows path is the C: volume."""
    return _drive_letter(path) == "C"


def per_user_case_root(environ=None) -> Path | None:
    """Return ``%LOCALAPPDATA%\\3DWET\\cases``, outside the program directory.

    The installer shortcut sets ``WET_USER_CASES=1`` so a machine with only C:
    still keeps user cases out of ``Programs\\3DWET``. A non-C: volume remains
    preferred and this folder is not used then.
    """
    env = os.environ if environ is None else environ
    local = str(env.get("LOCALAPPDATA", "")).strip()
    if not local:
        profile = str(env.get("USERPROFILE", "")).strip()
        if profile and os.name == "nt":
            local = str(Path(profile) / "AppData" / "Local")
    if not local:
        return None
    return Path(local).expanduser() / "3DWET" / "cases"


def _storage_key(path: str | Path) -> str:
    text = os.fspath(path).replace("/", "\\").rstrip("\\")
    if _drive_letter(text) and os.name != "nt":
        return os.path.normcase(text)
    try:
        return os.path.normcase(os.path.abspath(text))
    except (OSError, ValueError):
        return os.path.normcase(text)


def path_is_under(child: str | Path, parent: str | Path) -> bool:
    left = _storage_key(child)
    right = _storage_key(parent)
    return left == right or left.startswith(right + "\\")


def _user_cases_requested(env) -> bool:
    return str(env.get("WET_USER_CASES", "")).strip().lower() in {"1", "true", "yes", "on"}


def case_request_is_read_only_allowed(case_path: str | Path, method: str, route: str) -> bool:
    """Gate API writes for cases on C: while preserving safe read/copy actions.

    The installer's per-user folder may sit on C: when the machine has no
    other volume. That folder is outside the install directory and is writable.
    Other C: paths stay read-only.
    """
    if not is_system_drive(case_path):
        return True
    per_user = per_user_case_root()
    if per_user is not None and path_is_under(case_path, per_user):
        return True
    method = method.upper()
    if method in {"GET", "HEAD", "OPTIONS"}:
        return True
    return (method, route) in _READ_ONLY_CASE_POSTS


_WINDOWS_DRIVE = re.compile(r"^[A-Za-z]:[\\/]")


def _is_windows_drive_path(path: Path) -> bool:
    """True for ``D:\\...`` or ``D:/...`` before pathlib turns it into a relative name."""
    return _WINDOWS_DRIVE.match(os.fspath(path)) is not None


def _windows_drive_usable(path: Path) -> bool:
    """A drive letter is usable only on Windows, and never when it is C:."""
    if not _is_windows_drive_path(path):
        return True
    if os.name != "nt":
        return False
    letter = os.fspath(path)[0].upper()
    if letter == "C":
        return False
    return Path(f"{letter}:\\").exists()


def _probe_writable(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix=".wet-storage-check-", dir=path,
                                     delete=True):
        pass


def resolve_case_storage(base_dir: str | Path, environ=None):
    """Return (case_root, source, warning).

    Generated cases stay off C: whenever another volume can be written. The
    installer sets ``WET_USER_CASES=1``; if every non-C: volume is missing,
    cases then go to the per-user folder outside the install directory.
    A small write probe is used because a mounted path can exist while still
    being unwritable. The probe is removed immediately and never touches any
    existing case content.
    """
    env = os.environ if environ is None else environ
    configured = str(env.get("WET_CASE_DIR", "")).strip()
    candidates = []
    warnings = []
    if configured:
        path = Path(configured).expanduser()
        if is_system_drive(path):
            warnings.append(f"Ignoring WET_CASE_DIR={path}: C: storage is disabled for generated data.")
        else:
            candidates.append((path, "configured"))
    candidates.append((PREFERRED_CASE_ROOT, "preferred"))
    # If D: is unavailable, try existing non-system volumes using the same
    # application-specific folder. No C: candidate is ever considered.
    if os.name == "nt":
        for letter in "DEFGHIJKLMNOPQRSTUVWXYZ":
            drive_root = Path(f"{letter}:\\")
            if drive_root.exists():
                candidates.append((drive_root / "GETM-FABM-WET-outputs" / "cases",
                                   "alternate-volume"))

    checked = set()
    for candidate, source in candidates:
        if not _windows_drive_usable(candidate):
            letter = _drive_letter(candidate)
            if letter == "C":
                warnings.append(
                    f"Ignoring case root {candidate}: C: storage is disabled for generated data.")
            elif os.name != "nt" and letter:
                warnings.append(
                    f"Ignoring {candidate}: Windows drive paths are not used on this system.")
            else:
                warnings.append(f"Case root {candidate} unavailable: drive is not present.")
            continue
        try:
            path = candidate.resolve()
            key = os.path.normcase(str(path))
            if key in checked:
                continue
            checked.add(key)
            if is_system_drive(path):
                warnings.append(f"Ignoring case root {path}: C: storage is disabled for generated data.")
                continue
            _probe_writable(path)
            warning = " ".join(warnings) or None
            return path, source, warning
        except (OSError, RuntimeError, ValueError) as error:
            warnings.append(f"Case root {candidate} unavailable: {error}.")

    # Installer launches ask for a data directory outside Programs\3DWET.
    # Source checkouts leave WET_USER_CASES unset and keep the tree below.
    if _user_cases_requested(env):
        per_user = per_user_case_root(env)
        base = Path(base_dir)
        if per_user is not None and not path_is_under(per_user, base):
            try:
                _probe_writable(per_user)
                warnings.append(
                    "No non-C: volume is available; user cases are outside the install directory.")
                return per_user, "per-user", " ".join(warnings)
            except (OSError, RuntimeError, ValueError) as error:
                warnings.append(f"Per-user case root {per_user} unavailable: {error}.")

    # Linux and a Windows checkout without D: keep the restored cases in the
    # repository tree. Never resolve ``D:\`` as a relative directory: NetCDF
    # cannot create files in a path that still contains backslashes.
    base = Path(base_dir)
    if not _is_windows_drive_path(base):
        repo_case = base / "case"
        try:
            path = repo_case.resolve()
            _probe_writable(path)
            warning = " ".join(warnings) or None
            return path, "repository", warning
        except (OSError, RuntimeError, ValueError) as error:
            warnings.append(f"Case root {repo_case} unavailable: {error}.")

    detail = " ".join(warnings)
    raise OSError("No writable non-C: case storage is available. Connect a writable "
                  "non-C: drive or set WET_CASE_DIR to a writable non-C: folder. " + detail)


def resolve_state_storage(case_root: str | Path, environ=None):
    """Resolve writable app/case state under a non-C: root."""
    env = os.environ if environ is None else environ
    configured = str(env.get("WET_CASE_STATE_DIR", "")).strip()
    fallback = Path(case_root) / ".state"
    warnings = []
    candidates = []
    if configured:
        path = Path(configured).expanduser()
        if is_system_drive(path):
            warnings.append(f"Ignoring WET_CASE_STATE_DIR={path}: C: state storage is disabled.")
        else:
            candidates.append((path, "configured"))
    candidates.append((fallback, "default"))
    checked = set()
    for candidate, _source in candidates:
        try:
            path = candidate.resolve()
            key = os.path.normcase(str(path))
            if key in checked:
                continue
            checked.add(key)
            per_user = per_user_case_root(env)
            on_system = is_system_drive(path)
            if on_system and not (per_user is not None and path_is_under(path, per_user)):
                warnings.append(f"Ignoring state root {path}: C: state storage is disabled.")
                continue
            _probe_writable(path)
            return path, " ".join(warnings) or None
        except (OSError, RuntimeError, ValueError) as error:
            warnings.append(f"State root {candidate} unavailable: {error}.")
    raise OSError("No writable non-C: state storage is available. Set "
                  "WET_CASE_STATE_DIR to a writable non-C: folder. " + " ".join(warnings))

