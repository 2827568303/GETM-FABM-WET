"""Shared entry point for browser, WebView2 desktop, and diagnostic launches."""
from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path
import re
import sys
import threading
import time
import tempfile
import uuid
import webbrowser

from urllib.request import ProxyHandler, build_opener

from runtime import (LocalService, ModelRootLease, diagnostics, register_system_routes,
                     resolve_model_root, wait_until_ready)
from case_storage import is_system_drive, resolve_case_storage, resolve_state_storage


CLOSE_NOTICE = ('模型或率定任务仍在运行。请先在运行控制中停止任务，或等待任务完成，'
                '然后再关闭 3DWET Studio。服务将继续运行。')


class ShutdownGuard:
    """Serialize shutdown with mutating requests so a late start cannot be lost."""
    def __init__(self, backend):
        self.backend = backend
        self.lock = threading.RLock()
        self.closing = False

    def active(self):
        if getattr(self.backend, 'run_status', None) == 'running':
            return True
        thread = getattr(self.backend, 'run_thread', None)
        if thread is not None and thread.is_alive():
            return True
        calibration = sys.modules.get('calibration')
        if calibration is not None:
            with calibration._job_lock:
                for job in calibration.calibration_jobs.values():
                    thread = getattr(job, '_thread', None)
                    if job.status == 'running' or (thread is not None and thread.is_alive()):
                        return True
        return False

    def begin_shutdown(self):
        with self.lock:
            if self.active():
                return False
            self.closing = True
            return True

    def __call__(self, environ, start_response):
        if environ.get('REQUEST_METHOD') in ('GET', 'HEAD', 'OPTIONS'):
            return self.backend.app(environ, start_response)
        with self.lock:
            if self.closing:
                body = b'{"error":"Studio is shutting down. Reopen the application."}'
                start_response('503 Service Unavailable', [('Content-Type', 'application/json'),
                                                         ('Content-Length', str(len(body)))])
                return [body]
            return self.backend.app(environ, start_response)


def emit_report(report, destination=None):
    contents = json.dumps(report, indent=2, ensure_ascii=False)
    if destination:
        Path(destination).parent.mkdir(parents=True, exist_ok=True)
        Path(destination).write_text(contents + '\n', encoding='utf-8')
    # Windowed/frozen builds have no console stream. The report file remains
    # authoritative there; avoid turning a successful self-test into an error.
    if sys.stdout is not None:
        try:
            print(contents, file=sys.stdout, flush=True)
        except (OSError, ValueError):
            pass


def run_self_test(url, root, report):
    """Exercise the bundled application through real read-only HTTP requests."""
    from solver_runtime import inspect_runtime
    import calibration  # noqa: F401 -- packaging must include this lazy module
    import tkinter  # noqa: F401 -- folder chooser must survive freezing
    checks = {'imports': ['calibration', 'tkinter'], 'http': {}}
    report['self_test'] = checks
    opener = build_opener(ProxyHandler({}))

    def fetch(path, json_response=False):
        with opener.open(url + path, timeout=30) as response:
            data = response.read()
            checks['http'][path] = response.status
            if response.status != 200:
                raise RuntimeError(f'Self-test HTTP {path} returned {response.status}.')
            if json_response:
                json.loads(data)
            return data

    home = fetch('/').decode('utf-8')
    assets = sorted(set(re.findall(r'(?:src|href)=[\"\'](/static/[^\"\']+)', home)))
    if not assets or not any('.css' in path for path in assets) or not any('.js' in path for path in assets):
        raise RuntimeError('Self-test home page did not include CSS and JavaScript assets.')
    for path in assets:
        fetch(path)
    for path in ('/api/system/health', '/api/system/diagnostics', '/api/cases',
                 '/api/run/status', '/api/calibration/points', '/api/preprocess/help'):
        fetch(path, json_response=True)
    solver = root / 'bin' / ('getm_cartesian.exe' if os.name == 'nt' else 'getm_cartesian')
    runtime_report = inspect_runtime(solver, probe=True)
    report['solver']['runtime'] = runtime_report
    report['solver']['runtime_verified'] = runtime_report.get('loader_verified', False)
    checks['passed'] = bool(runtime_report.get('ready') and runtime_report.get('loader_verified'))
    return 0 if checks['passed'] else 1


class UiSmoke:
    """Verify the actual WebView document and bridge, then close an idle test window."""
    SCRIPT = """(async () => {
        try {
            const [healthResponse, runResponse] = await Promise.all([
                fetch('/api/system/health'), fetch('/api/run/status')]);
            const health = await healthResponse.json();
            const run = await runResponse.json();
            const layout = document.querySelector('.app-layout');
            const rect = layout && layout.getBoundingClientRect();
            await window.StudioI18n?.ready;
            const languageReady = !!(window.StudioI18n && document.getElementById('studio-language-button') && window.StudioI18n.languages().some(item => item.locale === 'en-US'));
            return {
                ready_state: document.readyState,
                hero_count: document.querySelectorAll('.studio-hero').length,
                bridge_ready: !!(window.pywebview && window.pywebview.api),
                layout_visible: !!(rect && rect.width > 0 && rect.height > 0),
                health_ready: healthResponse.ok && health.ready === true,
                application: health.application,
                model_root: health.model_root,
                instance_id: health.instance_id,
                model_status: runResponse.ok ? run.status : 'unknown',
                title: document.title,
                language_ready: languageReady,
                scripts: {chart: !!window.Chart, plotly: !!window.Plotly, leaflet: !!window.L}
            };
        } catch (error) { return {error: String(error)}; }
    })()"""

    def __init__(self, window, guard, report, destination):
        self.window = window
        self.guard = guard
        self.report = report
        self.destination = destination
        self.done = threading.Event()
        self.lock = threading.Lock()
        self.timer = threading.Timer(30, self.timed_out)
        self.timer.daemon = True
        self.report['ui_smoke'] = {'passed': False, 'renderer': 'edgechromium'}

    def start(self):
        self.timer.start()

    def cancel(self):
        self.timer.cancel()

    def loaded(self):
        try:
            self.window.evaluate_js(self.SCRIPT, callback=self.complete)
        except Exception as error:
            self.finish({'passed': False, 'error': str(error)})

    def complete(self, data):
        data = dict(data) if isinstance(data, dict) else {'error': 'WebView returned no DOM result.'}
        data['passed'] = (data.get('ready_state') == 'complete' and data.get('hero_count') == 0
                          and data.get('bridge_ready') is True and data.get('layout_visible') is True
                          and data.get('health_ready') is True and data.get('application') == '3dwet-studio'
                          and all(data.get('scripts', {}).get(name) is True for name in ('chart', 'plotly', 'leaflet'))
                          and data.get('model_status') in ('idle', 'completed', 'failed', 'stopped')
                          and (not self.report.get('model_root') or
                               os.path.normcase(data.get('model_root', '')) ==
                               os.path.normcase(self.report['model_root'])))
        if not data['passed'] and 'error' not in data:
            data['error'] = 'Rendered document, JavaScript bridge, local health, or idle model check failed.'
        self.finish(data)

    def timed_out(self):
        self.finish({'passed': False, 'error': 'WebView did not finish its DOM/health checks within 30 seconds.'})

    def finish(self, result):
        with self.lock:
            if self.done.is_set():
                return
            close_idle = self.guard is None or self.guard.begin_shutdown()
            if not close_idle:
                result.update(passed=False, error='Model or calibration is active; test window was kept open.')
            self.report['ui_smoke'].update(result)
            try:
                emit_report(self.report, self.destination)
            except Exception as error:
                self.report['ui_smoke'].update(passed=False, error=f'Cannot save UI smoke report: {error}')
                logging.exception('Could not save UI smoke report')
            self.done.set()
            self.cancel()
        if close_idle:
            try:
                self.window.destroy()
            except Exception:
                logging.exception('Could not close the UI smoke window')


def install_seed_cases(model_root, case_root):
    """Copy packaged examples into an empty user case folder once.

    The installer shortcut sets ``WET_USER_CASES``. Existing ``getm.inp`` files
    are left untouched, and the copy is skipped when the user folder is the
    packaged tree itself.
    """
    flag = os.environ.get('WET_USER_CASES', '').strip().lower()
    if flag not in {'1', 'true', 'yes', 'on'}:
        return
    source_root = Path(model_root) / 'case'
    destination_root = Path(case_root)
    try:
        if source_root.resolve() == destination_root.resolve():
            return
    except OSError:
        return
    if not source_root.is_dir():
        return
    for child in sorted(source_root.iterdir()):
        if not child.is_dir() or child.name.startswith('.'):
            continue
        destination = destination_root / child.name
        if (destination / 'getm.inp').is_file() or (destination / 'fabm.yaml').is_file():
            continue
        try:
            _copy_seed_tree(child, destination)
        except OSError:
            logging.exception('Could not copy seed case %s', child.name)


def _copy_seed_tree(source, destination):
    """Copy a seed case without Win32 CopyFile2.

    CPython's ``shutil.copytree`` uses ``CopyFile2``. Wine 9 aborts the
    process on that call, so the installed shortcut would never reach the
    server during the Wine smoke. A byte copy keeps the same files.
    """
    destination.mkdir(parents=True, exist_ok=False)
    for child in source.iterdir():
        name = child.name
        if name in {'output', '__pycache__'} or name == 'output.nc' or name.endswith('.log'):
            continue
        target = destination / name
        if child.is_dir() and not child.is_symlink():
            _copy_seed_tree(child, target)
        elif child.is_file():
            target.write_bytes(child.read_bytes())


def show_close_notice(window=None):
    if window is not None:
        window.create_confirmation_dialog('3DWET Studio', CLOSE_NOTICE)
    else:
        print(CLOSE_NOTICE, flush=True)


def configure_logging(directory=None):
    directory = Path(directory) if directory is not None else (
        Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / '3DWET Studio' / 'logs')
    directory.mkdir(parents=True, exist_ok=True)
    for name in ('stdout', 'stderr'):
        if getattr(sys, name, None) is None:
            setattr(sys, name, open(directory / 'launcher.log', 'a', encoding='utf-8', buffering=1))
    logging.basicConfig(filename=str(directory / 'launcher.log'), level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')
    return directory / 'launcher.log'


def main(argv=None):
    probe_args = list(sys.argv[1:] if argv is None else argv)
    if probe_args and probe_args[0] == '--mpi-dims-probe':
        if len(probe_args) != 4:
            raise SystemExit('invalid internal MPI dimensions probe arguments')
        from contextlib import redirect_stdout
        from mpi_runner import _MSMPI_DIMS_PROBE
        _, mpi_dll, counts, output_path = probe_args
        sys.argv = ['mpi-dims-probe', mpi_dll, counts]
        try:
            with open(output_path, 'w', encoding='utf-8') as output, redirect_stdout(output):
                exec(compile(_MSMPI_DIMS_PROBE, '<mpi-dims-probe>', 'exec'), {})
        except Exception as exc:
            Path(output_path).write_text('ERROR: ' + str(exc), encoding='utf-8')
            return 1
        return 0
    parser = argparse.ArgumentParser(description='3DWET Studio')
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--web', action='store_true', help='Open in the default browser')
    modes.add_argument('--desktop', action='store_true', help='Open a Windows WebView2 window')
    modes.add_argument('--check', action='store_true', help='Print dependencies and model paths')
    modes.add_argument('--self-test', action='store_true', help='Check packaged HTTP, imports and solver loader without UI')
    modes.add_argument('--ui-smoke', action='store_true', help='Open EdgeChromium, verify rendered UI and close the idle test window')
    parser.add_argument('--port', type=int, default=None)
    parser.add_argument('--no-open', action='store_true', help='Serve without opening a browser/window')
    parser.add_argument('--report', type=Path, help='Write diagnostic or smoke-test JSON to an absolute path')
    args = parser.parse_args(argv)
    if getattr(sys, 'frozen', False) and not args.web and not args.check and not args.self_test:
        args.desktop = True
    if args.ui_smoke:
        args.desktop = True
        if args.report is None or args.no_open:
            parser.error('--ui-smoke requires --report <absolute path> and opens a test window')
    if args.report is not None and (not args.report.is_absolute() or not (args.check or args.self_test or args.ui_smoke)):
        parser.error('--report requires an absolute path and --check, --self-test or --ui-smoke')
    if args.report is not None and is_system_drive(args.report):
        parser.error('--report must be saved outside C:')
    if args.port is not None and not 0 <= args.port <= 65535:
        parser.error('--port must be between 0 and 65535')
    log_path = None
    service = None
    lease = None
    guard = None
    report = None
    try:
        root = resolve_model_root()
        os.environ['WET_MODEL_ROOT'] = str(root)
        case_root, case_source, case_warning = resolve_case_storage(root)
        install_seed_cases(root, case_root)
        state_root, state_warning = resolve_state_storage(case_root)
        temp_root = case_root / '.temp'
        temp_root.mkdir(parents=True, exist_ok=True)
        tempfile.tempdir = str(temp_root)
        os.environ['TMP'] = str(temp_root)
        os.environ['TEMP'] = str(temp_root)
        os.environ['WET_CASE_DIR'] = str(case_root)
        os.environ['WET_CASE_STATE_DIR'] = str(state_root)
        os.environ['WET_CASE_STORAGE_SOURCE'] = case_source
        os.environ['WET_CASE_STORAGE_WARNING'] = ' '.join(filter(None, (case_warning, state_warning)))
        log_path = configure_logging(case_root / '.logs')
        report = diagnostics(root)
        if args.check:
            emit_report(report, args.report)
            return 0 if (all(report['dependencies'].values()) and report['solver']['exists'] and
                         report['solver'].get('runtime', {}).get('ready', True)) else 1
        missing = [package for package, present in report['dependencies'].items()
                   if not present and (package != 'pywebview' or args.desktop)]
        if missing:
            raise RuntimeError('Missing dependencies: ' + ', '.join(missing) + '. Run setup_studio.cmd.')
        lease = ModelRootLease(root, state_root=state_root)
        deadline = time.monotonic() + 30
        attached = None
        while not lease.acquire():
            try:
                attached = lease.existing_service(timeout=min(1, max(.01, deadline - time.monotonic())))
                break
            except TimeoutError:
                if time.monotonic() >= deadline:
                    raise
        if attached:
            if args.ui_smoke:
                raise RuntimeError('UI smoke needs its own idle model tree. Set WET_MODEL_ROOT to an unused staged model tree.')
            url = attached['url']
        else:
            import server
            server._reattach_orphan_model()
            guard = ShutdownGuard(server)
            if args.ui_smoke and guard.active():
                raise RuntimeError('UI smoke requires an idle model tree; a model or calibration is already running.')
            instance_id = uuid.uuid4().hex
            register_system_routes(server.app, root, instance_id)
            port = args.port if args.port is not None else (0 if args.desktop or args.self_test else 8766)
            try:
                service = LocalService(guard, port=port)
            except OSError as error:
                raise RuntimeError(f'Cannot bind 127.0.0.1:{port}; another process may own the port. '
                                   'Close that process or use --port 0.') from error
            service.start()
            wait_until_ready(service.url, instance_id, 30, root)
            lease.publish(service.url, instance_id)
            url = service.url
        print(f'3DWET Studio ready: {url}', flush=True)
        if args.self_test:
            result = run_self_test(url, root, report)
            emit_report(report, args.report)
            return result
        if args.desktop and not args.no_open:
            import webview
            window = webview.create_window('3DWET Studio', url, width=1440, height=960,
                                          min_size=(1024, 700))
            from desktop_notifications import install_notification_permission
            notification_permission = install_notification_permission(window, url)
            if guard is not None:
                def on_closing():
                    if not guard.begin_shutdown():
                        try:
                            show_close_notice(window)
                        except Exception:
                            logging.exception('Could not display the active-model close notice')
                        return False
                window.events.closing += on_closing
            smoke = UiSmoke(window, guard, report, args.report) if args.ui_smoke else None
            if smoke is not None:
                window.events.loaded += smoke.loaded
                smoke.start()
            try:
                webview.start(gui='edgechromium' if os.name == 'nt' else None)
            finally:
                if smoke is not None:
                    smoke.cancel()
                if notification_permission is not None:
                    notification_permission.release()
            if smoke is not None:
                if not smoke.done.is_set():
                    smoke.finish({'passed': False, 'error': 'Test window closed before UI checks completed.'})
                return 0 if report['ui_smoke']['passed'] else 1
        else:
            if not args.no_open:
                webbrowser.open(url)
            if attached:
                return 0
            print('Keep this console open. Press Ctrl+C to stop.', flush=True)
            while True:
                try:
                    if not service.thread.is_alive():
                        break
                    service.thread.join(timeout=.5)
                except KeyboardInterrupt:
                    if guard.begin_shutdown():
                        break
                    show_close_notice()
        return 0
    except KeyboardInterrupt:
        if args.ui_smoke:
            failure = report or {'application': '3dwet-studio'}
            failure['ui_smoke'] = {'passed': False, 'error': 'UI smoke was interrupted.'}
            emit_report(failure, args.report)
            return 1
        return 0
    except Exception as error:
        logging.exception('Studio launch failed')
        message = f'{error}' + (f'\nLog: {log_path}' if log_path else '')
        print(message, file=sys.stderr, flush=True)
        if args.check or args.self_test or args.ui_smoke:
            failure = report or {'application': '3dwet-studio'}
            failure['error'] = str(error)
            if args.self_test:
                failure.setdefault('self_test', {})['passed'] = False
            if args.ui_smoke:
                failure.setdefault('ui_smoke', {})['passed'] = False
            emit_report(failure, args.report)
        if args.desktop and not args.no_open and not args.ui_smoke and os.name == 'nt':
            import ctypes
            ctypes.windll.user32.MessageBoxW(None, message, '3DWET Studio - Startup error', 0x10)
        return 1
    finally:
        if service is not None:
            # A failed UI or repeated interrupt must not abandon an active solver.
            while guard is not None and not guard.begin_shutdown():
                show_close_notice()
                try:
                    time.sleep(.5)
                except KeyboardInterrupt:
                    continue
            service.stop()
        if lease is not None:
            lease.close()


if __name__ == '__main__':
    raise SystemExit(main())
