import importlib
import json
import os
from pathlib import Path
import sys
import socket
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from unittest.mock import patch
from unittest.mock import Mock, MagicMock
import subprocess
from types import SimpleNamespace

APP = Path(__file__).resolve().parents[1] / '3DWET' / 'app'
sys.path.insert(0, str(APP))


class RuntimeTests(unittest.TestCase):
    def runtime(self):
        self.assertIsNotNone(importlib.util.find_spec('runtime'), 'runtime module must exist')
        return importlib.import_module('runtime')

    def test_source_root_is_independent_of_cwd(self):
        runtime = self.runtime()
        with tempfile.TemporaryDirectory() as cwd, patch.dict(os.environ, {}, clear=True):
            old = os.getcwd()
            try:
                os.chdir(cwd)
                self.assertEqual(runtime.resolve_model_root(), APP.parent)
            finally:
                os.chdir(old)

    def test_explicit_missing_root_is_rejected(self):
        runtime = self.runtime()
        with tempfile.TemporaryDirectory() as root:
            with patch.dict(os.environ, {'WET_MODEL_ROOT': str(Path(root) / 'missing')}):
                with self.assertRaises(FileNotFoundError):
                    runtime.resolve_model_root()

    def test_frozen_finds_adjacent_model_tree(self):
        runtime = self.runtime()
        with tempfile.TemporaryDirectory() as root, patch.dict(os.environ, {}, clear=True):
            root = Path(root)
            (root / '3DWET' / 'bin').mkdir(parents=True)
            (root / '3DWET' / 'case').mkdir()
            with patch.object(sys, 'frozen', True, create=True), patch.object(sys, 'executable', str(root / 'Studio.exe')):
                self.assertEqual(runtime.resolve_model_root(), root / '3DWET')

    def test_health_rejects_foreign_and_wrong_instance(self):
        runtime = self.runtime()
        response = {'application': 'foreign', 'instance_id': 'ours', 'ready': True}
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            def log_message(self, *args):
                pass
        server = HTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            url = f'http://127.0.0.1:{server.server_port}'
            with self.assertRaises(runtime.ServiceIdentityError):
                runtime.wait_until_ready(url, 'ours', timeout=0.5)
            response['application'] = runtime.APPLICATION_ID
            response['instance_id'] = 'other'
            with self.assertRaises(runtime.ServiceIdentityError):
                runtime.wait_until_ready(url, 'ours', timeout=0.5)
            response['instance_id'] = 'ours'
            self.assertTrue(runtime.wait_until_ready(url, 'ours', timeout=0.5)['ready'])
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_owned_service_health_and_shutdown(self):
        runtime = self.runtime()
        from flask import Flask
        app = Flask(__name__)
        runtime.register_system_routes(app, APP.parent, 'test-instance')
        service = runtime.LocalService(app, port=0)
        service.start()
        try:
            self.assertTrue(runtime.wait_until_ready(service.url, 'test-instance')['ready'])
            with app.test_client() as client:
                report = client.get('/api/system/diagnostics').get_json()
                self.assertIn('dependencies', report)
                self.assertIn('solver', report)
        finally:
            service.stop()
        self.assertFalse(service.thread.is_alive())

    def test_occupied_port_is_not_attached(self):
        runtime = self.runtime()
        from flask import Flask
        server = HTTPServer(('127.0.0.1', 0), BaseHTTPRequestHandler)
        try:
            with self.assertRaises(OSError):
                runtime.LocalService(Flask(__name__), port=server.server_port)
        finally:
            server.server_close()

    def test_model_root_lease_blocks_second_owner_and_recovers(self):
        runtime = self.runtime()
        with tempfile.TemporaryDirectory() as folder:
            one = runtime.ModelRootLease(Path(folder))
            two = runtime.ModelRootLease(Path(folder))
            try:
                self.assertTrue(one.acquire())
                self.assertFalse(two.acquire())
                one.close()
                self.assertTrue(two.acquire())
            finally:
                one.close(); two.close()

    def test_shared_state_uses_separate_leases_for_different_model_roots(self):
        runtime = self.runtime()
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            state = base / 'shared-case-state'
            roots = [base / 'model-a', base / 'model-b']
            leases = [runtime.ModelRootLease(root, state_root=state) for root in roots]
            try:
                self.assertTrue(leases[0].acquire())
                leases[0].publish('http://127.0.0.1:1234', 'model-a')
                # A second model root must not interpret the legacy registry
                # as its own service or overwrite the first model's identity.
                self.assertTrue(leases[1].acquire())
                self.assertNotEqual(leases[0].directory, leases[1].directory)
                self.assertEqual(json.loads(leases[0].record.read_text())['model_root'],
                                 str(roots[0].resolve()))
                self.assertFalse(leases[1].record.exists())
                leases[1].publish('http://127.0.0.1:1235', 'model-b')
                self.assertEqual(json.loads(leases[1].record.read_text())['model_root'],
                                 str(roots[1].resolve()))
                self.assertTrue(leases[0].record.exists())
            finally:
                for lease in leases:
                    lease.close()

    def test_lease_blocks_another_process_and_survives_stale_record(self):
        runtime = self.runtime()
        with tempfile.TemporaryDirectory() as folder:
            lease = runtime.ModelRootLease(Path(folder))
            self.assertTrue(lease.acquire())
            code = ("import sys;sys.path.insert(0,sys.argv[1]);from runtime import ModelRootLease;"
                    "from pathlib import Path;l=ModelRootLease(Path(sys.argv[2]));"
                    "print(l.acquire());l.close()")
            result = subprocess.run([sys.executable, '-c', code, str(APP), folder],
                                    capture_output=True, text=True, check=True)
            self.assertEqual(result.stdout.strip(), 'False')
            lease.publish('http://127.0.0.1:1234', 'old')
            lease.close()
            lease.record.write_text('{"url":"http://127.0.0.1:1234"}')
            self.assertTrue(lease.acquire())
            self.assertFalse(lease.record.exists())
            lease.close()

    def test_lease_attaches_same_root_identity_over_http(self):
        runtime = self.runtime()
        from flask import Flask
        with tempfile.TemporaryDirectory() as folder:
            one, two = [runtime.ModelRootLease(Path(folder)) for _ in range(2)]
            app = Flask(__name__)
            runtime.register_system_routes(app, Path(folder), 'owner')
            service = runtime.LocalService(app)
            try:
                self.assertTrue(one.acquire())
                service.start()
                one.publish(service.url, 'owner')
                self.assertFalse(two.acquire())
                record = two.existing_service(timeout=2)
                self.assertEqual(record['url'], service.url)
                self.assertEqual(record['model_root'], str(Path(folder).resolve()))
            finally:
                service.stop(); one.close(); two.close()

    def test_health_refuses_correct_instance_from_wrong_model_tree(self):
        runtime = self.runtime()
        from flask import Flask
        app = Flask(__name__)
        runtime.register_system_routes(app, APP.parent, 'same-id')
        service = runtime.LocalService(app)
        service.start()
        try:
            with self.assertRaises(runtime.ServiceIdentityError):
                runtime.wait_until_ready(service.url, 'same-id', model_root=APP, timeout=.5)
        finally:
            service.stop()

    def test_closing_guard_protects_model_and_calibration_threads(self):
        import launcher
        backend = Mock(run_status='running', run_thread=None)
        guard = launcher.ShutdownGuard(backend)
        self.assertFalse(guard.begin_shutdown())
        backend.run_status = 'completed'
        job = Mock(status='stopped', _thread=Mock())
        job._thread.is_alive.return_value = True
        calibration = Mock(calibration_jobs={'job': job}, _job_lock=threading.Lock())
        with patch.dict(sys.modules, {'calibration': calibration}):
            self.assertFalse(guard.begin_shutdown())
            job._thread.is_alive.return_value = False
            self.assertTrue(guard.begin_shutdown())

    def test_check_writes_report(self):
        import launcher
        report = {'dependencies': {}, 'solver': {'exists': True}, 'application': '3dwet-studio'}
        with patch.object(tempfile, 'tempdir', None), tempfile.TemporaryDirectory() as folder, \
                patch.object(launcher, 'configure_logging'), \
                patch.object(launcher, 'resolve_case_storage', return_value=(Path(folder) / 'cases', 'test', None)), \
                patch.object(launcher, 'resolve_state_storage', return_value=(Path(folder) / 'state', None)), \
                patch.object(launcher, 'is_system_drive', return_value=False), \
                patch.object(launcher, 'diagnostics', return_value=report):
            output = Path(folder) / 'check.json'
            self.assertEqual(launcher.main(['--check', '--report', str(output)]), 0)
            self.assertEqual(json.loads(output.read_text(encoding='utf-8')), report)

    def test_existing_service_waits_for_delayed_publication_and_refuses_lost_readiness(self):
        runtime = self.runtime()
        from flask import Flask
        with tempfile.TemporaryDirectory() as folder:
            one, two = [runtime.ModelRootLease(Path(folder)) for _ in range(2)]
            app = Flask(__name__)
            runtime.register_system_routes(app, Path(folder), 'owner')
            service = runtime.LocalService(app)
            try:
                self.assertTrue(one.acquire())
                service.start()
                publisher = threading.Timer(.1, one.publish, args=(service.url, 'owner'))
                publisher.start()
                self.assertEqual(two.existing_service(timeout=2)['url'], service.url)
                publisher.join()
                service.stop()
                with self.assertRaises(TimeoutError):
                    two.existing_service(timeout=.15)
            finally:
                if service.thread.is_alive():
                    service.stop()
                one.close(); two.close()

    def test_shutdown_rejects_a_late_model_start(self):
        import launcher
        from flask import Flask
        app = Flask(__name__)
        calls = []
        @app.post('/api/run/start')
        def start():
            calls.append('started')
            return {'ok': True}
        backend = Mock(app=app, run_status='idle', run_thread=None)
        guard = launcher.ShutdownGuard(backend)
        from werkzeug.test import Client
        self.assertTrue(guard.begin_shutdown())
        self.assertEqual(Client(guard).post('/api/run/start').status_code, 503)
        self.assertEqual(calls, [])

    def test_second_launcher_attaches_without_importing_or_stopping_backend(self):
        import launcher
        runtime = self.runtime()
        from flask import Flask
        with patch.object(tempfile, 'tempdir', None), tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            owner = runtime.ModelRootLease(root)
            owner.acquire()
            app = Flask(__name__)
            runtime.register_system_routes(app, root, 'existing')
            service = runtime.LocalService(app)
            service.start()
            owner.publish(service.url, 'existing')
            try:
                with patch.object(launcher, 'configure_logging'), \
                        patch.object(launcher, 'resolve_model_root', return_value=root), \
                        patch.object(launcher, 'resolve_case_storage', return_value=(root, 'test', None)), \
                        patch.object(launcher, 'resolve_state_storage', return_value=(root, None)), \
                        patch.object(launcher, 'diagnostics', return_value={'dependencies': {}}), \
                        patch.object(launcher, 'LocalService') as create, \
                        patch.object(launcher.webbrowser, 'open') as browser:
                    self.assertEqual(launcher.main(['--web']), 0)
                    create.assert_not_called()
                    browser.assert_called_once_with(service.url)
                self.assertTrue(service.thread.is_alive())
                self.assertTrue(owner.record.exists())
            finally:
                service.stop(); owner.close()

    def test_console_interrupt_keeps_active_model_until_completion(self):
        import launcher
        backend = Mock(app=Mock(), run_status='running', run_thread=None)
        service = Mock(url='http://127.0.0.1:12345')
        service.thread.is_alive.side_effect = [KeyboardInterrupt, True, KeyboardInterrupt]
        service.thread.join.side_effect = lambda **kwargs: setattr(backend, 'run_status', 'completed')
        with patch.object(tempfile, 'tempdir', None), tempfile.TemporaryDirectory() as folder, \
                patch.dict(sys.modules, {'server': backend}), \
                patch.object(launcher, 'configure_logging'), \
                patch.object(launcher, 'resolve_model_root', return_value=Path(folder)), \
                patch.object(launcher, 'resolve_case_storage', return_value=(Path(folder) / 'cases', 'test', None)), \
                patch.object(launcher, 'resolve_state_storage', return_value=(Path(folder) / 'state', None)), \
                patch.object(launcher, 'diagnostics', return_value={'dependencies': {}}), \
                patch.object(launcher, 'register_system_routes'), \
                patch.object(launcher, 'wait_until_ready'), \
                patch.object(launcher, 'LocalService', return_value=service), \
                patch.object(launcher, 'show_close_notice') as notice:
            self.assertEqual(launcher.main(['--web', '--no-open']), 0)
            notice.assert_called_once_with()
            service.thread.join.assert_called_once()
            service.stop.assert_called_once()

    def test_primary_desktop_close_veto_survives_dialog_failure(self):
        import launcher
        from webview.event import Event
        backend = Mock(app=Mock(), run_status='running', run_thread=None)
        service = Mock(url='http://127.0.0.1:12345')
        window = Mock()
        window.events = SimpleNamespace(closing=Event(window, True))
        view = Mock()
        view.create_window.return_value = window
        def close_twice(**kwargs):
            self.assertTrue(window.events.closing.set())
            service.stop.assert_not_called()
            backend.run_status = 'completed'
            self.assertFalse(window.events.closing.set())
        view.start.side_effect = close_twice
        with patch.object(tempfile, 'tempdir', None), tempfile.TemporaryDirectory() as folder, \
                patch.dict(sys.modules, {'server': backend, 'webview': view}), \
                patch.object(launcher, 'configure_logging'), \
                patch.object(launcher, 'resolve_model_root', return_value=Path(folder)), \
                patch.object(launcher, 'resolve_case_storage', return_value=(Path(folder) / 'cases', 'test', None)), \
                patch.object(launcher, 'resolve_state_storage', return_value=(Path(folder) / 'state', None)), \
                patch.object(launcher, 'diagnostics', return_value={'dependencies': {}}), \
                patch.object(launcher, 'register_system_routes'), \
                patch.object(launcher, 'wait_until_ready'), \
                patch.object(launcher, 'LocalService', return_value=service), \
                patch.object(launcher, 'show_close_notice', side_effect=RuntimeError('dialog unavailable')):
            self.assertEqual(launcher.main(['--desktop']), 0)
            service.stop.assert_called_once()

    def test_self_test_exercises_http_assets_and_core_apis(self):
        import launcher
        runtime = self.runtime()
        from flask import Flask
        app = Flask(__name__, static_folder=None)
        @app.get('/')
        def home():
            return '<link href="/static/test.css"><script src="/static/test.js"></script>'
        @app.get('/static/<path:asset>')
        def asset(asset):
            return 'asset'
        paths = ('/api/system/health', '/api/system/diagnostics', '/api/cases',
                 '/api/run/status', '/api/calibration/points', '/api/preprocess/help')
        for index, path in enumerate(paths):
            app.add_url_rule(path, f'api_{index}', lambda: {'ok': True})
        service = runtime.LocalService(app)
        service.start()
        try:
            report = {'solver': {}}
            with patch('solver_runtime.inspect_runtime', return_value={'ready': True, 'loader_verified': True}):
                self.assertEqual(launcher.run_self_test(service.url, APP.parent, report), 0)
            self.assertTrue(report['self_test']['passed'])
            self.assertEqual(len(report['self_test']['http']), len(paths) + 3)
            self.assertEqual(set(report['self_test']['http'].values()), {200})
        finally:
            service.stop()

    def test_ui_smoke_checks_browser_dom_and_health_before_closing(self):
        import launcher
        window = Mock()
        window.events = SimpleNamespace(loaded=SimpleNamespace())
        def evaluate(script, callback):
            self.assertIn('document.readyState', script)
            self.assertIn('.studio-hero', script)
            self.assertIn('/api/system/health', script)
            callback({'ready_state': 'complete', 'hero_count': 0, 'bridge_ready': True,
                      'layout_visible': True, 'health_ready': True, 'model_status': 'idle',
                      'application': '3dwet-studio',
                      'scripts': {'chart': True, 'plotly': True, 'leaflet': True}})
        window.evaluate_js.side_effect = evaluate
        backend = Mock(app=Mock(), run_status='idle', run_thread=None)
        with tempfile.TemporaryDirectory() as folder:
            report = {'application': '3dwet-studio'}
            smoke = launcher.UiSmoke(window, launcher.ShutdownGuard(backend), report,
                                     Path(folder) / 'ui.json')
            smoke.loaded()
            self.assertTrue(smoke.done.wait(1))
            self.assertTrue(report['ui_smoke']['passed'])
            window.destroy.assert_called_once()
            self.assertTrue((Path(folder) / 'ui.json').exists())
            smoke.cancel()

    def test_ui_smoke_timeout_reports_failure_and_closes_idle_window(self):
        import launcher
        window = Mock()
        backend = Mock(app=Mock(), run_status='idle', run_thread=None)
        with tempfile.TemporaryDirectory() as folder:
            report = {'application': '3dwet-studio'}
            smoke = launcher.UiSmoke(window, launcher.ShutdownGuard(backend), report,
                                     Path(folder) / 'ui.json')
            smoke.timed_out()
            self.assertFalse(report['ui_smoke']['passed'])
            self.assertIn('30', report['ui_smoke']['error'])
            window.destroy.assert_called_once()
            smoke.cancel()

    def test_attach_refuses_nonlocal_record(self):
        runtime = self.runtime()
        with tempfile.TemporaryDirectory() as folder:
            lease = runtime.ModelRootLease(Path(folder))
            lease.record.write_text(json.dumps({'url':'https://example.com', 'instance_id':'x'}))
            with self.assertRaises(runtime.ServiceIdentityError):
                lease.existing_service(timeout=.1)

    def test_shutdown_closes_idle_browser_connections(self):
        runtime = self.runtime()
        from flask import Flask
        app = Flask(__name__)
        runtime.register_system_routes(app, APP.parent, 'idle')
        service = runtime.LocalService(app)
        service.start()
        port = int(service.url.rsplit(':', 1)[1])
        connection = socket.create_connection(('127.0.0.1', port), timeout=2)
        try:
            connection.sendall(b'GET /api/system/health HTTP/1.1\r\nHost: localhost\r\nConnection: keep-alive\r\n\r\n')
            self.assertIn(b'200 OK', connection.recv(4096))
            service.stop()
            self.assertFalse(service.thread.is_alive())
        finally:
            connection.close()

    def test_idle_service_does_not_consume_a_cpu_core(self):
        runtime = self.runtime()
        from flask import Flask
        app = Flask(__name__)
        runtime.register_system_routes(app, APP.parent, 'idle-cpu')
        service = runtime.LocalService(app)
        service.start()
        try:
            started = time.process_time()
            time.sleep(1)
            idle_cpu = time.process_time() - started
            self.assertLess(idle_cpu, .5, f'Idle HTTP service consumed {idle_cpu:.3f} CPU seconds')
            from urllib.request import build_opener, ProxyHandler
            with build_opener(ProxyHandler({})).open(service.url + '/api/system/health', timeout=2) as response:
                self.assertEqual(response.status, 200)
        finally:
            service.stop()
        self.assertFalse(service.thread.is_alive())

    def test_launcher_waits_before_browser_open_and_stops_after_interrupt(self):
        import launcher
        events = []
        service = Mock(url='http://127.0.0.1:12345')
        service.start.side_effect = lambda: events.append('started')
        service.thread.is_alive.side_effect = KeyboardInterrupt
        with patch.object(tempfile, 'tempdir', None), tempfile.TemporaryDirectory() as folder, \
                patch.dict(sys.modules, {'server': Mock(app=Mock(), run_status='idle', run_thread=None)}), \
                patch.object(launcher, 'resolve_model_root', return_value=Path(folder)), \
                patch.object(launcher, 'configure_logging'), \
                patch.object(launcher, 'resolve_case_storage', return_value=(Path(folder) / 'cases', 'test', None)), \
                patch.object(launcher, 'resolve_state_storage', return_value=(Path(folder) / 'state', None)), \
                patch.object(launcher, 'diagnostics', return_value={'dependencies': {}}), \
                patch.object(launcher, 'register_system_routes'), \
                patch.object(launcher, 'LocalService', return_value=service), \
                patch.object(launcher, 'wait_until_ready', side_effect=lambda *a: events.append('ready')), \
                patch.object(launcher.webbrowser, 'open', side_effect=lambda *a: events.append('opened')):
            self.assertEqual(launcher.main(['--web']), 0)
        self.assertEqual(events, ['started', 'ready', 'opened'])
        service.stop.assert_called_once()

    def test_frozen_launch_defaults_to_desktop(self):
        import launcher
        service = Mock(url='http://127.0.0.1:12345')
        view = MagicMock()
        with patch.object(tempfile, 'tempdir', None), tempfile.TemporaryDirectory() as folder, \
                patch.dict(sys.modules, {'server': Mock(app=Mock(), run_status='idle', run_thread=None), 'webview': view}), \
                patch.object(sys, 'frozen', True, create=True), \
                patch.object(launcher, 'configure_logging'), \
                patch.object(launcher, 'resolve_model_root', return_value=Path(folder)), \
                patch.object(launcher, 'resolve_case_storage', return_value=(Path(folder) / 'cases', 'test', None)), \
                patch.object(launcher, 'resolve_state_storage', return_value=(Path(folder) / 'state', None)), \
                patch.object(launcher, 'diagnostics', return_value={'dependencies': {}}), \
                patch.object(launcher, 'register_system_routes'), \
                patch.object(launcher, 'LocalService', return_value=service), \
                patch.object(launcher, 'wait_until_ready'), \
                patch.object(launcher.webbrowser, 'open') as browser:
            service.thread.is_alive.side_effect = KeyboardInterrupt
            self.assertEqual(launcher.main([]), 0)
        view.create_window.assert_called_once()
        browser.assert_not_called()

    def test_windows_launch_defaults_to_desktop_without_web_flag(self):
        import launcher
        plain = SimpleNamespace(web=False, desktop=False, check=False, self_test=False, ui_smoke=False)
        web = SimpleNamespace(web=True, desktop=False, check=False, self_test=False, ui_smoke=False)
        self.assertTrue(launcher.launch_is_desktop(plain, frozen=False, platform='nt'))
        self.assertFalse(launcher.launch_is_desktop(web, frozen=False, platform='nt'))
        self.assertFalse(launcher.launch_is_desktop(plain, frozen=False, platform='posix'))
        self.assertTrue(launcher.launch_is_desktop(plain, frozen=True, platform='posix'))


if __name__ == '__main__':
    unittest.main()
