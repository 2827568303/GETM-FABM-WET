#!/usr/bin/env python3
"""Cross-platform runner for the repository JavaScript tests.

Mirrors 3DWET/tests/run-js-tests.ps1: node:test files run together, and
scripts that are not node:test run one at a time. Exits 0 only when every
file passes.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NODE_TEST = "node:test"


def test_files():
    found = list((ROOT / "3DWET" / "tests").glob("test_*.js"))
    tests = ROOT / "tests"
    if tests.is_dir():
        for path in tests.rglob("*"):
            if not path.is_file() or path.suffix not in {".js", ".cjs", ".mjs"}:
                continue
            if any(part in {"build", "CMakeFiles", "node_modules"} for part in path.parts):
                continue
            found.append(path)
    return sorted(found)


def main() -> int:
    files = test_files()
    node_tests = []
    standalone = []
    for path in files:
        source = path.read_text(encoding="utf-8", errors="replace")
        if NODE_TEST in source:
            node_tests.append(path)
        else:
            standalone.append(path)
    failed = []
    if node_tests:
        print(f"Running {len(node_tests)} node:test files", flush=True)
        result = subprocess.run(
            ["node", "--test", "--test-concurrency=1", "--test-timeout=10000",
             *[str(path) for path in node_tests]],
            cwd=ROOT)
        if result.returncode != 0:
            failed.append("node:test files")
    for path in standalone:
        print(f"Running {path.name}", flush=True)
        result = subprocess.run(["node", str(path)], cwd=ROOT)
        if result.returncode != 0:
            failed.append(path.name)
    if failed:
        print("JavaScript test failures: " + ", ".join(failed), file=sys.stderr)
        return 1
    print(f"All {len(files)} JavaScript test files passed (3DWET/tests + repository tests/).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
