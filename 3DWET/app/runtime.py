"""Runtime paths, diagnostics, and the owned loopback HTTP service."""
from __future__ import annotations

import importlib.util
import hashlib
import json
import os
import socket
from pathlib import Path
import sys
import threading
import time
import tempfile
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import ProxyHandler, build_opener

APPLICATION_ID = '3dwet-studio'
DEPENDENCIES = {
    'flask': 'Flask', 'numpy': 'numpy', 'scipy': 'scipy', 'netCDF4': 'netCDF4',
    'yaml': 'PyYAML', 'shapefile': 'pyshp', 'pyproj': 'pyproj',
    'psutil': 'psutil', 'waitress': 'waitress', 'webview': 'pywebview',
}


def resolve_model_root() -> Path:
    override = os.environ.get('WET_MODEL_ROOT')
    if override:
        candidates = [Path(override).expanduser().resolve()]
    elif getattr(sys, 'frozen', False):
        folder = Path(sys.executable).resolve().parent
        candidates = [folder / '3DWET', folder, folder.parent / '3DWET',
                      folder.parent.parent / '3DWET']
    else:
        candidates = [Path(__file__).resolve().parent.parent]
    for candidate in candidates:
        if (candidate / 'bin').is_dir() and (candidate / 'case').is_dir():
            return candidate
    raise FileNotFoundError('Model tree not found (requires bin and case directories). '
                            'Set WET_MODEL_ROOT to the writable 3DWET directory. '
                            f'Searched: {", ".join(map(str, candidates))}')


def diagnostics(model_root: Path) -> dict:
    dependencies = {package: importlib.util.find_spec(module) is not None
                    for module, package in DEPENDENCIES.items()}
    solver = model_root / 'bin' / ('getm_cartesian.exe' if os.name == 'nt' else 'getm_cartesian')
    from solver_runtime import inspect_runtime
    solver_runtime = inspect_runtime(solver)
    case_root = Path(os.environ.get('WET_CASE_DIR', r'D:\GETM-FABM-WET-outputs\cases'))
    state_root = Path(os.environ.get('WET_CASE_STATE_DIR', str(case_root / '.state')))
    return {'application': APPLICATION_ID, 'python': sys.version.split()[0],
            'frozen': bool(getattr(sys, 'frozen', False)), 'model_root': str(model_root),
            'case_storage': {'case_root': str(case_root),
                             'source': os.environ.get('WET_CASE_STORAGE_SOURCE', 'preferred'),
                             'fallback': os.environ.get('WET_CASE_STORAGE_SOURCE') == 'alternate-volume',
                             'warning': os.environ.get('WET_CASE_STORAGE_WARNING') or None,
                             'temporary_root': str(case_root / '.temp'),
                             'log_root': str(case_root / '.logs'),
                             'state_root': str(state_root)},
            'writable': os.access(model_root, os.W_OK), 'dependencies': dependencies,
            'solver': {'path': str(solver), 'exists': solver.is_file(),
                       'runtime_verified': solver_runtime.get('loader_verified', False),
                       'runtime': solver_runtime,
                       'note': 'Loader verification does not verify scientific execution.'}}


def register_system_routes(app, model_root: Path, instance_id: str) -> None:
    from flask import jsonify, request
    state_root = Path(os.environ.get('WET_CASE_STATE_DIR', str(model_root / '.state')))
    preference_path = state_root / '.studio-runtime' / 'language.json'
    preference_lock = threading.Lock()

    @app.route('/api/system/language', methods=['GET', 'PUT'])
    def studio_language():
        # Desktop uses a new loopback port and a private WebView profile on each
        # launch. Keep its locale and packs with the application, not the port.
        if preference_path.is_symlink():
            return jsonify(error='Invalid preferences file.'), 400
        with preference_lock:
            if request.method == 'GET':
                try:
                    if preference_path.stat().st_size > 2 * 1024 * 1024:
                        raise ValueError('Preferences too large.')
                    return jsonify(json.loads(preference_path.read_text(encoding='utf-8')))
                except (OSError, ValueError):
                    return jsonify(locale='zh-CN', packs=[])
            if request.headers.get('Origin', request.host_url.rstrip('/')) != request.host_url.rstrip('/'):
                return jsonify(error='Same-origin request required.'), 403
            if request.content_length is None or request.content_length > 2 * 1024 * 1024:
                return jsonify(error='Language preferences too large.'), 413
            value = request.get_json(silent=True)
            if not isinstance(value, dict) or set(value) != {'locale', 'packs'} or not isinstance(value['locale'], str) or len(value['locale']) > 35 or not isinstance(value['packs'], list) or len(value['packs']) > 16:
                return jsonify(error='Invalid language preferences.'), 400
            try:
                preference_path.parent.mkdir(parents=True, exist_ok=True)
                with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=preference_path.parent, delete=False) as stream:
                    json.dump(value, stream, ensure_ascii=False)
                    temporary = Path(stream.name)
                os.replace(temporary, preference_path)
            except OSError:
                return jsonify(error='Could not save language preferences.'), 500
            return jsonify(saved=True)

    @app.get('/api/system/health')
    def studio_health():
        return jsonify(application=APPLICATION_ID, instance_id=instance_id,
                       model_root=str(model_root.resolve()), pid=os.getpid(), ready=True)

    @app.get('/api/system/diagnostics')
    def studio_diagnostics():
        return jsonify(diagnostics(model_root))


class ServiceIdentityError(RuntimeError):
    pass


def validate_local_url(url: str) -> None:
    try:
        parts = urlsplit(url)
        valid = (parts.scheme == 'http' and parts.hostname == '127.0.0.1' and
                 parts.port is not None and 1 <= parts.port <= 65535 and
                 parts.path in ('', '/') and not parts.username and not parts.password and
                 not parts.query and not parts.fragment)
    except (TypeError, ValueError):
        valid = False
    if not valid:
        raise ServiceIdentityError('Registry URL is not an owned local loopback service; refusing to connect.')


def wait_until_ready(url: str, instance_id: str, timeout: float = 30,
                     model_root: Path | None = None) -> dict:
    validate_local_url(url)
    deadline = time.monotonic() + timeout
    opener = build_opener(ProxyHandler({}))
    last_error = None
    while time.monotonic() < deadline:
        try:
            with opener.open(url + '/api/system/health', timeout=min(1, max(.05, timeout))) as response:
                health = json.load(response)
            if not isinstance(health, dict) or health.get('application') != APPLICATION_ID or health.get('instance_id') != instance_id:
                raise ServiceIdentityError('Port is serving a different application or instance; refusing to connect.')
            if model_root is not None and os.path.normcase(health.get('model_root', '')) != os.path.normcase(str(model_root.resolve())):
                raise ServiceIdentityError('Service belongs to a different model tree; refusing to connect.')
            if health.get('ready') is True:
                return health
        except (URLError, OSError, ValueError) as error:
            last_error = error
        time.sleep(.05)
    raise TimeoutError(f'Studio did not become ready at {url}: {last_error or "not ready"}')


class ModelRootLease:
    """OS-held ownership for one mutable backend per model tree.

    The lock file stays in place: removing it could create two lock identities.
    The registry is advisory and only trusted after an HTTP identity check.
    """
    def __init__(self, model_root: Path, state_root: Path | None = None):
        self.root = model_root.resolve()
        self.runtime_root = ((Path(state_root).resolve() if state_root else self.root)
                             / '.studio-runtime')
        self.directory = self.runtime_root
        self._use_model_scoped_directory = False
        self._set_registry_paths()
        self._file = None
        self.owned = False

    def _set_registry_paths(self):
        self.directory = (self.runtime_root / 'models' / self._model_key()
                          if self._use_model_scoped_directory else self.runtime_root)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.record = self.directory / 'service.json'

    def _model_key(self):
        identity = os.path.normcase(str(self.root))
        return hashlib.sha256(identity.encode('utf-8')).hexdigest()[:24]

    def _switch_to_model_scoped_directory(self):
        if self._file is not None:
            self._file.close()
            self._file = None
        self._use_model_scoped_directory = True
        self._set_registry_paths()

    def acquire(self) -> bool:
        if self.owned:
            return True
        if self._file is None:
            self._file = open(self.directory / 'owner.lock', 'a+b')
            # msvcrt requires a byte to exist; appending is safe before locking.
            if os.fstat(self._file.fileno()).st_size == 0:
                self._file.write(b'0')
                self._file.flush()
        self._file.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(self._file.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self._file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            # Older releases put every model's lease in the shared case-state
            # directory. Keep attaching to that registry when it belongs to
            # this model, but move aside when another model owns it.
            try:
                record = json.loads(self.record.read_text(encoding='utf-8'))
            except (OSError, ValueError):
                record = None
            if (isinstance(record, dict) and
                    os.path.normcase(record.get('model_root', '')) !=
                    os.path.normcase(str(self.root))):
                self._switch_to_model_scoped_directory()
                return self.acquire()
            return False
        self.owned = True
        self.record.unlink(missing_ok=True)
        return True

    def publish(self, url: str, instance_id: str):
        if not self.owned:
            raise RuntimeError('Only the backend owner can publish its service.')
        validate_local_url(url)
        record = {'application': APPLICATION_ID, 'url': url, 'instance_id': instance_id,
                  'pid': os.getpid(), 'model_root': str(self.root)}
        fd, filename = tempfile.mkstemp(prefix='service-', suffix='.tmp', dir=self.directory)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as output:
                json.dump(record, output)
                output.flush()
                os.fsync(output.fileno())
            os.replace(filename, self.record)
        finally:
            Path(filename).unlink(missing_ok=True)

    def existing_service(self, timeout: float = 30) -> dict:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                record = json.loads(self.record.read_text(encoding='utf-8'))
            except (OSError, ValueError):
                time.sleep(.05)
                continue
            if not isinstance(record, dict):
                raise ServiceIdentityError('Invalid service registry.')
            validate_local_url(record.get('url'))
            if (record.get('application') != APPLICATION_ID or
                    os.path.normcase(record.get('model_root', '')) != os.path.normcase(str(self.root)) or
                    not isinstance(record.get('instance_id'), str) or
                    not isinstance(record.get('pid'), int)):
                raise ServiceIdentityError('Registry identity does not match this model tree.')
            health = wait_until_ready(record['url'], record['instance_id'],
                                      timeout=max(.01, deadline - time.monotonic()), model_root=self.root)
            if health.get('pid') != record['pid']:
                raise ServiceIdentityError('Registry process does not match the local service.')
            return record
        raise TimeoutError('Another Studio owns this model tree but has not published a ready service.')

    def close(self):
        if self.owned:
            self.record.unlink(missing_ok=True)
            self._file.seek(0)
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(self._file.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self._file.fileno(), fcntl.LOCK_UN)
            self.owned = False
        if self._file is not None:
            self._file.close()
            self._file = None


class LocalService:
    """Own both the listening socket and its worker lifetime; never reuse another server."""
    def __init__(self, app, port: int = 0):
        from waitress import create_server
        # Windows SO_REUSEADDR permits duplicate listeners; reserve exclusively
        # before Waitress creates worker threads and pass the owned socket through.
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):
                listener.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            listener.bind(('127.0.0.1', port))
            # Waitress converts this setting to int; .1 becomes a zero-timeout
            # busy poll. Socket readiness and the shutdown trigger wake it early.
            self.server = create_server(app, sockets=[listener], threads=4,
                                        asyncore_loop_timeout=1)
        except Exception:
            listener.close()
            raise
        self.url = f'http://127.0.0.1:{self.server.effective_port}'
        self._stopping = threading.Event()
        self.thread = threading.Thread(target=self._run, name='studio-http', daemon=True)

    def _run(self):
        try:
            self.server.run()
        except OSError as error:
            # Closing retained browser sockets can interrupt select() on Windows.
            # Suppress only that expected shutdown race, never a serving error.
            if not self._stopping.is_set() or error.errno not in (9, 10038):
                raise

    def start(self):
        self.thread.start()

    def stop(self):
        self._stopping.set()
        # Let in-flight workers finish while their wakeup trigger is still alive.
        self.server.task_dispatcher.shutdown()
        # Browsers retain idle HTTP connections after closing their window.
        # These channels must close too, otherwise the asyncore loop stays alive.
        from waitress import wasyncore
        wasyncore.close_all(map=self.server._map)
        if self.thread.ident is not None:
            self.thread.join(timeout=5)
        if self.thread.is_alive():
            raise RuntimeError('The local HTTP service failed to stop.')
