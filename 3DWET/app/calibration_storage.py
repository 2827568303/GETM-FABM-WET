"""Read-only packaged calibration seeds and writable user calibration storage."""
import json
import os
from pathlib import Path


def migrate_missing_files(legacy_dir, user_dir, filenames):
    """Copy legacy files to user storage once, preserving existing user edits."""
    legacy_dir = Path(legacy_dir)
    user_dir = Path(user_dir)
    migrated = []
    for filename in filenames:
        source = legacy_dir / filename
        target = user_dir / filename
        if not source.is_file():
            continue
        try:
            descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o666)
        except FileExistsError:
            continue
        with os.fdopen(descriptor, "wb") as destination, source.open("rb") as origin:
            destination.write(origin.read())
        migrated.append(filename)
    return migrated


def load_json_with_seed(user_path, seed_path, default):
    """Load writable user JSON first, then an immutable source-tree seed."""
    user_path = Path(user_path)
    seed_path = Path(seed_path)
    source = user_path if user_path.is_file() else seed_path
    if source.is_file():
        with source.open("r", encoding="utf-8") as stream:
            return json.load(stream)
    return default
