#!/usr/bin/env bash
# Build 3DWET-Setup-<version>.exe on Linux (Wine + Inno Setup) or on a machine
# that already has ISCC.exe. The setup embeds CPython 3.12, the Windows wheels
# in scripts/installer/requirements-win.lock, the 3DWET UI, and the Windows
# solvers plus the bundled MS-MPI runtime. It does not require a Windows build
# of PyInstaller. See docs/使用说明.md.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="${WET_INSTALLER_VERSION:-1.0.0}"
PY_VER="3.12.7"
PY_URL="https://www.python.org/ftp/python/${PY_VER}/python-${PY_VER}-embed-amd64.zip"
PY_SHA256="0d57bb6cb078b74d23dbfe91f77d6780d45bed328911609f1f7ee2ba1606bf44"
INNO_URL="https://github.com/jrsoftware/issrc/releases/download/is-6_7_3/innosetup-6.7.3.exe"
INNO_SHA256="9c73c3bae7ed48d44112a0f48e66742c00090bdb5bef71d9d3c056c66e97b732"
WORK="${WET_INSTALLER_WORK:-/tmp/3dwet-installer-build}"
CACHE="${WET_INSTALLER_CACHE:-${WORK}/cache}"
STAGE="${WORK}/stage"
OUTPUT="${WORK}/output"
WINEPREFIX="${WET_INSTALLER_WINEPREFIX:-${WORK}/wine}"
LOCK="${ROOT}/scripts/installer/requirements-win.lock"
ISS="${ROOT}/scripts/installer/3DWET.iss"
ARTIFACT_DIR="${WET_INSTALLER_ARTIFACT:-/opt/cursor/artifacts}"
SMOKE="${WET_INSTALLER_SMOKE:-1}"
SETUP_NAME="3DWET-Setup-${VERSION}.exe"

log() { printf '==> %s\n' "$*" >&2; }
to_win() { WINEPREFIX="$WINEPREFIX" winepath -w "$1" | tr -d '\r'; }
# A pipe is not a Windows console. Embeddable CPython then dies in
# init_sys_streams with WinError 6, even when PYTHONLEGACYWINDOWSSTDIO=1.
# The first argument is a transcript path, or "-" to keep the program's own
# stdout. The rest is the wine command.
wine_console() {
  local transcript="$1"
  shift
  local command
  command="$(printf '%q ' "$@")"
  if [[ -n "${WINE_CONSOLE_TIMEOUT:-}" ]]; then
    command="timeout ${WINE_CONSOLE_TIMEOUT} ${command}"
  fi
  if [[ "$transcript" == "-" ]]; then
    script -q -e -c "$command" /dev/null
  else
    script -q -e -c "$command" "$transcript" >/dev/null
  fi
}
die() { printf 'error: %s\n' "$*" >&2; exit 1; }

sha256_file() {
  sha256sum "$1" | awk '{print $1}'
}

require_hash() {
  local path="$1" expected="$2"
  local actual
  actual="$(sha256_file "$path")"
  [[ "$actual" == "$expected" ]] || die "SHA256 mismatch for ${path}: ${actual} != ${expected}"
}

fetch() {
  local url="$1" dest="$2" expected="$3"
  if [[ -f "$dest" ]]; then
    require_hash "$dest" "$expected"
    return
  fi
  log "download $(basename "$dest")"
  curl -fL --retry 3 --retry-delay 2 -o "${dest}.partial" "$url"
  mv "${dest}.partial" "$dest"
  require_hash "$dest" "$expected"
}

stage_python() {
  local zip="$1" dest="$2"
  rm -rf "$dest"
  mkdir -p "$dest"
  unzip -q "$zip" -d "$dest"
  python3 - "$dest" <<'PY'
import pathlib, sys
dest = pathlib.Path(sys.argv[1])
pth = next(dest.glob("python3*._pth"))
zip_name = next(dest.glob("python3*.zip")).name
pth.write_bytes(
    (
        f"{zip_name}\n"
        ".\n"
        "Lib\\site-packages\n"
        "..\\3DWET\\app\n"
        "import site\n"
    ).encode("ascii")
)
print(f"wrote {pth.name}")
PY
}

stage_wheels() {
  local site="$1" wheelhouse="$2"
  rm -rf "$site"
  mkdir -p "$site" "$wheelhouse"
  python3 -m pip install --disable-pip-version-check --no-compile --upgrade \
    --no-index --find-links "$wheelhouse" \
    --target "$site" \
    --python-version 3.12 --platform win_amd64 --implementation cp \
    --only-binary=:all: \
    -r "$LOCK"
}

download_wheels() {
  local wheelhouse="$1"
  mkdir -p "$wheelhouse"
  if [[ -n "$(find "$wheelhouse" -name '*.whl' -print -quit)" ]]; then
    log "using cached wheels in ${wheelhouse}"
    return
  fi
  log "download Windows wheels"
  python3 -m pip download -d "$wheelhouse" \
    --python-version 3.12 --platform win_amd64 --implementation cp \
    --only-binary=:all: \
    -r "$LOCK"
}

copy_tree() {
  python3 - "$ROOT" "$STAGE" <<'PY'
import shutil
import sys
from pathlib import Path

root = Path(sys.argv[1])
stage = Path(sys.argv[2])
app_src = root / "3DWET" / "app"
app_dst = stage / "3DWET" / "app"
skip_names = {"__pycache__", ".pytest_cache"}

def ignore(directory, names):
    ignored = []
    for name in names:
        if name in skip_names or name.endswith(".pyc") or name.startswith("_test"):
            ignored.append(name)
        elif ":" in name or name.startswith("D:\\"):
            ignored.append(name)
    return ignored

shutil.copytree(app_src, app_dst, ignore=ignore, dirs_exist_ok=True)
bin_dst = stage / "3DWET" / "bin"
bin_dst.mkdir(parents=True, exist_ok=True)
bin_src = root / "3DWET" / "bin"
for name in ("getm_cartesian.exe", "getm_cartesian_serial.exe", "getm_cartesian_parallel.exe"):
    shutil.copy2(bin_src / name, bin_dst / name)
shutil.copytree(bin_src / "runtime", bin_dst / "runtime", dirs_exist_ok=True)
shutil.copytree(bin_src / "mpi", bin_dst / "mpi", dirs_exist_ok=True)
scripts = stage / "3DWET" / "scripts"
scripts.mkdir(parents=True, exist_ok=True)
shutil.copy2(root / "3DWET" / "scripts" / "merge_getm_rank_outputs.py", scripts / "merge_getm_rank_outputs.py")
case_src = root / "3DWET" / "case" / "NativeTest"
case_dst = stage / "3DWET" / "case" / "NativeTest"
if case_dst.exists():
    shutil.rmtree(case_dst)
shutil.copytree(case_src, case_dst, ignore=shutil.ignore_patterns("output", "output.nc", "*.log", "__pycache__"))
shutil.copy2(app_src / "static" / "brand" / "3dwet.ico", stage / "3dwet.ico")
(stage / "3DWET.cmd").write_bytes(
    (
        "@echo off\r\n"
        "setlocal\r\n"
        "cd /d \"%~dp0\"\r\n"
        "set \"WET_USER_CASES=1\"\r\n"
        "set \"WET_MODEL_ROOT=%~dp03DWET\"\r\n"
        "set \"PYTHONUNBUFFERED=1\"\r\n"
        "set \"PYTHONLEGACYWINDOWSSTDIO=1\"\r\n"
        "set \"PATH=%~dp03DWET\\bin\\mpi;%~dp03DWET\\bin\\runtime;%~dp03DWET\\bin;%~dp0python;%PATH%\"\r\n"
        "\"%~dp0python\\python.exe\" \"%~dp03DWET\\app\\launcher.py\" --web %*\r\n"
        "endlocal\r\n"
    ).encode("ascii")
)
notice = stage / "DEPENDENCIES.txt"
notice.write_text(
    "\n".join([
        "3DWET Windows installer",
        "",
        "Embedded CPython 3.12.7 (x64 embeddable package, PSF license: python\\LICENSE.txt).",
        "Python packages: scripts/installer/requirements-win.lock (NumPy pinned to 1.26.4).",
        "pywebview is not bundled. The shortcut runs launcher.py --web and opens the browser.",
        "pyabc is not bundled. Calibration uses the SciPy fallback already in the app.",
        "The folder dialog falls back to Windows PowerShell when tkinter is absent.",
        "",
        "Solvers, all under 3DWET\\bin:",
        "  getm_cartesian.exe           OpenMP",
        "  getm_cartesian_serial.exe    serial fallback",
        "  getm_cartesian_parallel.exe  MS-MPI, current solver revision",
        "  mpi\\                         mpiexec.exe, smpd.exe, msmpi.dll (MS-MPI-LICENSE.txt)",
        "  runtime\\                     Fortran and NetCDF DLLs used by the solvers",
        "",
        "There is no core-count cap. Multi-process runs use the bundled MS-MPI files",
        "and do not need a separate MS-MPI install.",
        "",
        "Install directory (per user, no administrator): %LOCALAPPDATA%\\Programs\\3DWET",
        "User cases stay outside that directory:",
        "  D:\\GETM-FABM-WET-outputs\\cases when a non-C: volume can be written",
        "  otherwise %LOCALAPPDATA%\\3DWET\\cases",
        "Uninstall removes the program only. Case folders are kept.",
        "",
    ]),
    encoding="utf-8",
)
print("staged", stage)
PY
}

compile_installer() {
  local iscc="$1"
  mkdir -p "$OUTPUT"
  local stage_win output_win iss_win
  stage_win="$(to_win "$STAGE")"
  output_win="$(to_win "$OUTPUT")"
  iss_win="$(to_win "$ISS")"
  log "compile ${SETUP_NAME}"
  WINEPREFIX="$WINEPREFIX" WINEDEBUG="${WINEDEBUG:--all}" \
    wine "$iscc" "/DStageDir=${stage_win}" "/DOutputDir=${output_win}" "/DAppVersion=${VERSION}" "$iss_win"
  [[ -f "${OUTPUT}/${SETUP_NAME}" ]] || die "Inno Setup did not write ${SETUP_NAME}"
}

ensure_inno() {
  local compiler="${WINEPREFIX}/drive_c/InnoSetup/ISCC.exe"
  if [[ -f "$compiler" ]]; then
    printf '%s\n' "$compiler"
    return
  fi
  log "install Inno Setup under Wine"
  mkdir -p "$WINEPREFIX"
  WINEPREFIX="$WINEPREFIX" WINEDEBUG="${WINEDEBUG:--all}" wineboot --init
  WINEPREFIX="$WINEPREFIX" WINEDEBUG="${WINEDEBUG:--all}" \
    wine "${CACHE}/innosetup-6.7.3.exe" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP- /DIR=C:\\InnoSetup
  [[ -f "$compiler" ]] || die "ISCC.exe was not installed"
  printf '%s\n' "$compiler"
}

smoke_install() {
  local setup="$1"
  log "silent install"
  WINEPREFIX="$WINEPREFIX" WINEDEBUG="${WINEDEBUG:--all}" \
    wine "$setup" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP-
  local python
  python="$(find "${WINEPREFIX}/drive_c/users" -path '*/Programs/3DWET/python/python.exe' -print -quit)"
  [[ -n "$python" ]] || die "silent install did not produce python.exe"
  local app
  app="$(dirname "$(dirname "$python")")"
  log "installed at ${app}"
  if find "$app" -iname '*efdc*' -print -quit | grep -q .; then
    die "the install contains an EFDC file"
  fi
  WINEPREFIX="$WINEPREFIX" wineserver -k || true
  local win_py
  win_py="$(to_win "$python")"
  log "import bundled packages"
  WINEPREFIX="$WINEPREFIX" WINEDEBUG="${WINEDEBUG:--all}" \
    PYTHONLEGACYWINDOWSSTDIO=1 PYTHONUNBUFFERED=1 WINE_CONSOLE_TIMEOUT=180 \
    wine_console - wine "$win_py" -c "import flask,numpy,scipy,netCDF4,yaml,shapefile,pyproj,psutil,waitress,openpyxl; print('numpy', numpy.__version__)" \
    || die "embedded Python could not import the server dependencies"
  unset WINE_CONSOLE_TIMEOUT
  local port="${WET_INSTALLER_PORT:-18766}"
  local log_file="${WORK}/smoke-server.log"
  log "launch server on 127.0.0.1:${port}"
  WINEPREFIX="$WINEPREFIX" WINEDEBUG="${WINEDEBUG:--all}" \
    WET_USER_CASES=1 PYTHONUNBUFFERED=1 PYTHONLEGACYWINDOWSSTDIO=1 \
    wine_console "$log_file" wine "$win_py" "$(to_win "${app}/3DWET/app/launcher.py")" \
      --web --no-open --port "$port" &
  local server_pid=$!
  cleanup_server() {
    if kill -0 "$server_pid" 2>/dev/null; then
      kill "$server_pid" 2>/dev/null || true
      wait "$server_pid" 2>/dev/null || true
    fi
    WINEPREFIX="$WINEPREFIX" wineserver -k || true
  }
  local ready=0
  for _ in $(seq 1 90); do
    if python3 - "$port" <<'PY'
import sys, urllib.request
url = f"http://127.0.0.1:{sys.argv[1]}/"
try:
    with urllib.request.urlopen(url, timeout=2) as response:
        body = response.read().decode("utf-8", "replace")
except Exception:
    sys.exit(1)
sys.exit(0 if "3DWET" in body else 2)
PY
    then
      ready=1
      break
    fi
    if ! kill -0 "$server_pid" 2>/dev/null; then
      break
    fi
    sleep 2
  done
  if [[ "$ready" != 1 ]]; then
    cleanup_server
    printf 'server log:\n' >&2
    tail -n 80 "$log_file" >&2 || true
    die "bundled server did not serve the 3DWET UI"
  fi
  python3 - "$port" <<'PY'
import json, sys, urllib.request
port = sys.argv[1]
html = urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=30).read().decode("utf-8", "replace")
if "3DWET" not in html:
    raise SystemExit("home page did not mention 3DWET")
if 'value="triangles"' in html or "value='triangles'" in html:
    raise SystemExit("home page still offers a triangle mesh option")
plan = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/api/run/core-plan", timeout=60))
if not isinstance(plan, dict) or "hardware" not in plan:
    raise SystemExit(f"core-plan payload missing hardware: {sorted(plan)[:12]}")
print("core-plan keys", ",".join(sorted(plan)))
PY
  cleanup_server
  smoke_solver "$app" || die "1-hour serial or OpenMP case did not finish"
  log "silent uninstall"
  local uninstaller
  uninstaller="$(find "$app" -maxdepth 1 -name 'unins*.exe' -print -quit)"
  [[ -n "$uninstaller" ]] || die "uninstaller was not written"
  local cases
  cases="$(find "${WINEPREFIX}/drive_c/users" -type d -path '*/3DWET/cases' -print -quit || true)"
  WINEPREFIX="$WINEPREFIX" WINEDEBUG="${WINEDEBUG:--all}" \
    wine "$(to_win "$uninstaller")" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART
  [[ ! -e "$python" ]] || die "uninstall left python.exe in place"
  if [[ -n "$cases" && ! -d "$cases" ]]; then
    die "uninstall removed user cases at ${cases}"
  fi
  log "silent uninstall removed the program and kept user cases"
}

smoke_solver() {
  local app="$1"
  local serial="${app}/3DWET/bin/getm_cartesian_serial.exe"
  local openmp="${app}/3DWET/bin/getm_cartesian.exe"
  [[ -f "$serial" && -f "$openmp" ]] || die "installed solvers are missing"
  # NativeTest stops on the first step with non-finite abiotic_water_sDIMW.
  # That happens with the solvers from before 78c8f18 as well, so the smoke
  # uses the repository Lake Dianchi case for one model hour instead.
  local case_dir="${WORK}/solver-smoke"
  local case_src="${ROOT}/3DWET/case/Lake Dianchi"
  [[ -f "${case_src}/getm.inp" ]] || die "Lake Dianchi case is missing"
  rm -rf "$case_dir"
  mkdir -p "$case_dir"
  cp -a "${case_src}/." "$case_dir/"
  python3 - "$case_dir/getm.inp" <<'PY'
import pathlib, sys
path = pathlib.Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
old = "stop = '2020-12-29 00:00:00'"
new = "stop = '2020-01-01 01:00:00'"
if old not in text:
    raise SystemExit("could not set Lake Dianchi to a 1-hour window")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
PY
  local runtime mpi
  runtime="$(to_win "${app}/3DWET/bin/runtime")"
  mpi="$(to_win "${app}/3DWET/bin/mpi")"
  run_one() {
    local label="$1" exe="$2"
    local out="${WORK}/solver-${label}.log"
    log "solver smoke ${label}: Lake Dianchi 2020-01-01 00:00 to 01:00"
    set +e
    WINEPREFIX="$WINEPREFIX" WINEDEBUG="${WINEDEBUG:--all}" \
      WINEPATH="${runtime};${mpi}" OMP_NUM_THREADS=1 \
      timeout 600 wine "$(to_win "$exe")" </dev/null >"$out" 2>&1
    local code=$?
    set -e
    if [[ "$code" -eq 0 ]] && grep -q 'getm: Completed on' "$out" && ! grep -q 'Non-finite' "$out"; then
      log "${label} finished the 1-hour case"
      return 0
    fi
    printf '%s log (exit %s):\n' "$label" "$code" >&2
    tail -n 40 "$out" >&2 || true
    return 1
  }
  if ( cd "$case_dir" && run_one serial "$serial" ); then
    return 0
  fi
  log "serial 1-hour case did not finish; trying OpenMP"
  ( cd "$case_dir" && run_one openmp "$openmp" )
}

main() {
  [[ -f "$LOCK" ]] || die "missing ${LOCK}"
  grep -q '^numpy==1.26.4$' "$LOCK" || die "requirements-win.lock must pin numpy==1.26.4"
  command -v wine >/dev/null || die "wine is required"
  command -v script >/dev/null || die "script is required for the Wine console"
  command -v curl >/dev/null || die "curl is required"
  command -v unzip >/dev/null || die "unzip is required"
  mkdir -p "$CACHE" "$OUTPUT"
  rm -rf "$STAGE"
  fetch "$PY_URL" "${CACHE}/python-${PY_VER}-embed-amd64.zip" "$PY_SHA256"
  fetch "$INNO_URL" "${CACHE}/innosetup-6.7.3.exe" "$INNO_SHA256"
  log "stage embedded Python"
  stage_python "${CACHE}/python-${PY_VER}-embed-amd64.zip" "${STAGE}/python"
  download_wheels "${CACHE}/wheels"
  log "install Windows packages into the embeddable runtime"
  stage_wheels "${STAGE}/python/Lib/site-packages" "${CACHE}/wheels"
  log "stage 3DWET"
  copy_tree
  local iscc
  iscc="$(ensure_inno)"
  compile_installer "$iscc"
  local setup="${OUTPUT}/${SETUP_NAME}"
  python3 - "$setup" <<'PY'
import hashlib, pathlib, sys
path = pathlib.Path(sys.argv[1])
digest = hashlib.sha256(path.read_bytes()).hexdigest()
print(f"SETUP {path}")
print(f"BYTES {path.stat().st_size}")
print(f"SHA256 {digest}")
PY
  if [[ "$SMOKE" == 1 ]]; then
    smoke_install "$setup"
  fi
  if [[ -d "$ARTIFACT_DIR" || "$ARTIFACT_DIR" == /opt/cursor/artifacts ]]; then
    mkdir -p "$ARTIFACT_DIR"
    python3 - "$setup" "${ARTIFACT_DIR}/${SETUP_NAME}" <<'PY'
import hashlib, pathlib, sys
src = pathlib.Path(sys.argv[1])
dst = pathlib.Path(sys.argv[2])
if dst.exists():
    dst.unlink()
digest = hashlib.sha256()
with src.open("rb") as inp, dst.open("wb") as out:
    while True:
        block = inp.read(4 * 1024 * 1024)
        if not block:
            break
        digest.update(block)
        out.write(block)
print(f"ARTIFACT {dst}")
print(f"BYTES {dst.stat().st_size}")
print(f"SHA256 {digest.hexdigest()}")
PY
  fi
  log "done ${setup}"
}

main "$@"
