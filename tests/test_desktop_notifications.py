"""Notification policy and host lifetime checks; no native windows are opened."""
from pathlib import Path
import importlib
import importlib.util
import os
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest


APP = Path(__file__).resolve().parents[1] / '3DWET' / 'app'
sys.path.insert(0, str(APP))
ORIGIN = 'http://127.0.0.1:59117'
ALLOW, DENY, NOTIFICATIONS = 'allow', 'deny', 'notifications'


def test_desktop_notification_host_module_exists():
    assert importlib.util.find_spec('desktop_notifications') is not None, (
        'Desktop WebView2 notification permission handling is missing')


@pytest.fixture
def notifications():
    assert importlib.util.find_spec('desktop_notifications') is not None, (
        'Desktop WebView2 notification permission handling is missing')
    return importlib.import_module('desktop_notifications')


class Request:
    def __init__(self, uri=ORIGIN, kind=NOTIFICATIONS):
        self.Uri = uri
        self.PermissionKind = kind
        self.State = 'default'
        self.SavesInProfile = True
        self.Handled = False
        self.deferral = SimpleNamespace(Complete=Mock())
        self.GetDeferral = Mock(return_value=self.deferral)


def controller(module, answer=True, current_url=ORIGIN):
    pending = []
    prompt = Mock(return_value=answer)
    location = SimpleNamespace(url=current_url)
    policy = module.NotificationPermissionController(
        ORIGIN, current_uri=lambda: location.url, prompt=prompt,
        schedule=pending.append, notification_kind=NOTIFICATIONS,
        allow_state=ALLOW, deny_state=DENY)
    return policy, pending, prompt, location


def test_prompt_is_deferred_and_only_explicit_yes_allows(notifications):
    policy, pending, prompt, _ = controller(notifications)
    request = Request(ORIGIN + '/?page=run')
    policy.requested(None, request)
    prompt.assert_not_called()
    assert request.State == DENY
    assert request.Handled is True and request.SavesInProfile is False
    assert len(pending) == 1
    request.deferral.Complete.assert_not_called()
    pending.pop()()
    prompt.assert_called_once_with(ORIGIN)
    assert request.State == ALLOW
    request.deferral.Complete.assert_called_once()


@pytest.mark.parametrize('answer', [False, None, 1, 'yes'])
def test_no_cancel_or_non_boolean_result_never_allows(notifications, answer):
    policy, pending, _, _ = controller(notifications, answer)
    request = Request()
    policy.requested(None, request)
    pending.pop()()
    assert request.State == DENY
    request.deferral.Complete.assert_called_once()


@pytest.mark.parametrize('uri', [
    'http://127.0.0.1:59118', 'https://127.0.0.1:59117',
    'http://localhost:59117', 'http://127.0.0.1.evil:59117',
    'http://127.0.0.1.:59117', 'http://127.1:59117',
    'http://user@127.0.0.1:59117', 'http://127.0.0.1:59117@evil.test',
    'http://evil.test', 'file:///tmp/page', 'data:text/plain,hello',
    'http://127.0.0.1:invalid', 'http://127.0.0.1:59117\\@evil.test',
    'http://127.0.0.1:59117\n', 'http://127.0.0.1:59117\x00', '', None,
])
def test_other_origins_and_malformed_uris_are_denied_without_prompt(notifications, uri):
    policy, pending, prompt, _ = controller(notifications)
    request = Request(uri)
    policy.requested(None, request)
    assert request.State == DENY
    assert request.SavesInProfile is False
    assert request.Handled is True
    assert pending == []
    prompt.assert_not_called()
    request.GetDeferral.assert_not_called()


def test_other_permissions_are_left_untouched(notifications):
    policy, pending, prompt, _ = controller(notifications)
    request = Request('https://external.test', 'camera')
    policy.requested(None, request)
    assert request.State == 'default'
    assert request.Handled is False and request.SavesInProfile is True
    assert pending == []
    prompt.assert_not_called()
    request.GetDeferral.assert_not_called()


@pytest.mark.parametrize('answer, expected', [(True, ALLOW), (False, DENY)])
def test_repeated_requests_share_a_single_session_choice(notifications, answer, expected):
    policy, pending, prompt, _ = controller(notifications, answer)
    requests = [Request(), Request(ORIGIN + '/other')]
    for request in requests:
        policy.requested(None, request)
    assert len(pending) == 1
    pending.pop()()
    for request in requests:
        assert request.State == expected
        request.deferral.Complete.assert_called_once()
    later = Request()
    policy.requested(None, later)
    assert later.State == expected and later.SavesInProfile is False
    later.GetDeferral.assert_not_called()
    prompt.assert_called_once()
    assert pending == []
    fresh, new_queue, new_prompt, _ = controller(notifications)
    fresh.requested(None, Request())
    assert len(new_queue) == 1
    new_prompt.assert_not_called()


def test_reentrant_request_during_prompt_is_completed_by_same_choice(notifications):
    policy, pending, prompt, _ = controller(notifications)
    nested = Request()
    prompt.side_effect = lambda origin: (policy.requested(None, nested) or True)
    first = Request()
    policy.requested(None, first)
    pending.pop()()
    assert pending == []
    assert first.State == nested.State == ALLOW
    nested.deferral.Complete.assert_called_once()
    prompt.assert_called_once()


@pytest.mark.parametrize('phase', ['before_request', 'before_prompt', 'during_prompt'])
def test_navigation_out_of_bound_origin_prevents_grant(notifications, phase):
    policy, pending, prompt, location = controller(notifications)
    if phase == 'before_request':
        location.url = 'https://external.test'
    request = Request()
    policy.requested(None, request)
    if phase == 'before_prompt':
        location.url = 'https://external.test'
    elif phase == 'during_prompt':
        def navigate(origin):
            location.url = 'https://external.test'
            return True
        prompt.side_effect = navigate
    if pending:
        pending.pop()()
        request.deferral.Complete.assert_called_once()
    assert request.State == DENY
    if phase != 'during_prompt':
        prompt.assert_not_called()


def test_disposal_denies_pending_requests_and_scheduled_prompt_stays_inert(notifications):
    policy, pending, prompt, _ = controller(notifications)
    request = Request()
    policy.requested(None, request)
    policy.close()
    policy.close()
    request.deferral.Complete.assert_called_once()
    pending.pop()()
    prompt.assert_not_called()
    later = Request()
    policy.requested(None, later)
    assert later.State == DENY
    later.GetDeferral.assert_not_called()
    request.deferral.Complete.assert_called_once()


def test_disposal_during_prompt_cannot_grant_or_complete_twice(notifications):
    policy, pending, prompt, _ = controller(notifications)
    prompt.side_effect = lambda origin: (policy.close() or True)
    request = Request()
    policy.requested(None, request)
    pending.pop()()
    assert request.State == DENY
    request.deferral.Complete.assert_called_once()


@pytest.mark.parametrize('failure', ['schedule', 'prompt', 'deferral', 'persistence'])
def test_host_failures_deny_and_are_logged(notifications, failure, caplog):
    policy, pending, prompt, _ = controller(notifications)
    request = Request()
    if failure == 'schedule':
        policy.schedule = Mock(side_effect=RuntimeError('UI queue unavailable'))
    elif failure == 'prompt':
        prompt.side_effect = RuntimeError('dialog unavailable')
    elif failure == 'deferral':
        request.GetDeferral.side_effect = RuntimeError('deferral unavailable')
    elif failure == 'persistence':
        class LegacyRequest(Request):
            @property
            def SavesInProfile(self):
                return True

            @SavesInProfile.setter
            def SavesInProfile(self, value):
                if value is False:
                    raise RuntimeError('session-only permission unsupported')
        request = LegacyRequest()
    policy.requested(None, request)
    if pending:
        pending.pop()()
    assert request.State == DENY
    assert 'notification' in caplog.text.lower()
    if failure in ('schedule', 'prompt'):
        request.deferral.Complete.assert_called_once()
    if failure != 'prompt':
        prompt.assert_not_called()


class Event:
    def __init__(self):
        self.handlers = []

    def __iadd__(self, handler):
        self.handlers.append(handler)
        return self

    def __isub__(self, handler):
        self.handlers.remove(handler)
        return self

    def emit(self, *args):
        for handler in list(self.handlers):
            handler(*args)


def fake_window(ready=False):
    core = SimpleNamespace(PermissionRequested=Event(), Source=ORIGIN)
    control = SimpleNamespace(CoreWebView2=core if ready else None,
                              CoreWebView2InitializationCompleted=Event(), Disposed=Event(),
                              BeginInvoke=Mock(), IsDisposed=False)
    window = SimpleNamespace(native=SimpleNamespace(webview=control, FormClosed=Event()),
                             events=SimpleNamespace(before_show=Event()))
    api = SimpleNamespace(notification_kind=NOTIFICATIONS, allow_state=ALLOW,
                          deny_state=DENY, action=lambda callback: callback,
                          confirm=Mock(return_value=True))
    return window, control, core, api


@pytest.mark.parametrize('ready', [False, True])
def test_binding_installs_on_ui_before_show_handles_initialization_and_detaches(notifications, ready):
    window, control, core, api = fake_window(ready)
    with patch.object(notifications, '_load_webview2', return_value=api):
        binding = notifications.install_notification_permission(window, ORIGIN)
        assert core.PermissionRequested.handlers == []
        window.events.before_show.emit()
        if not ready:
            assert core.PermissionRequested.handlers == []
            control.CoreWebView2 = core
            control.CoreWebView2InitializationCompleted.emit(control, SimpleNamespace(IsSuccess=True))
        assert len(core.PermissionRequested.handlers) == 1
        control.CoreWebView2InitializationCompleted.emit(control, SimpleNamespace(IsSuccess=True))
        assert len(core.PermissionRequested.handlers) == 1
        request = Request()
        core.PermissionRequested.emit(core, request)
        api.confirm.assert_not_called()
        control.BeginInvoke.assert_called_once()
        control.BeginInvoke.call_args.args[0]()
        assert request.State == ALLOW
        api.confirm.assert_called_once_with(window.native, ORIGIN)
        control.Disposed.emit(control, None)
        assert core.PermissionRequested.handlers == []
        assert control.CoreWebView2InitializationCompleted.handlers == []
        assert control.Disposed.handlers == []
        assert window.native.FormClosed.handlers == []
        assert window.events.before_show.handlers == []
        binding.close()


def test_form_closed_cleans_up_in_sta_even_when_control_disposed_did_not_fire(notifications):
    window, control, core, api = fake_window(True)
    with patch.object(notifications, '_load_webview2', return_value=api):
        binding = notifications.install_notification_permission(window, ORIGIN)
        window.events.before_show.emit()
        request = Request()
        core.PermissionRequested.emit(core, request)
        window.native.FormClosed.emit(window.native, None)
        request.deferral.Complete.assert_called_once()
        assert request.State == DENY
        assert core.PermissionRequested.handlers == []
        assert control.Disposed.handlers == []
        binding.release()
        request.deferral.Complete.assert_called_once()


def test_after_loop_fallback_does_not_touch_native_events_or_deferrals(notifications):
    window, control, core, api = fake_window(True)
    with patch.object(notifications, '_load_webview2', return_value=api):
        binding = notifications.install_notification_permission(window, ORIGIN)
        window.events.before_show.emit()
        request = Request()
        core.PermissionRequested.emit(core, request)
        # Simulate the UI loop having terminated without delivering disposal.
        class UnavailableNative:
            def __getattr__(self, name):
                pytest.fail('Native state accessed from after-loop fallback: ' + name)
        binding.control = binding.core = UnavailableNative()
        binding.subscriptions = [
            (owner if owner is window.events else UnavailableNative(), name, handler)
            for owner, name, handler in binding.subscriptions]
        binding.release()
        binding.release()
        request.deferral.Complete.assert_not_called()
        control.BeginInvoke.call_args.args[0]()
        api.confirm.assert_not_called()
        assert binding.closed is True
        assert window.events.before_show.handlers == []


def test_failed_initialization_never_attaches_and_logs(notifications, caplog):
    window, control, core, api = fake_window()
    with patch.object(notifications, '_load_webview2', return_value=api):
        binding = notifications.install_notification_permission(window, ORIGIN)
        window.events.before_show.emit()
        control.CoreWebView2InitializationCompleted.emit(
            control, SimpleNamespace(IsSuccess=False, InitializationException='unavailable'))
        assert core.PermissionRequested.handlers == []
        assert 'notification' in caplog.text.lower()
        binding.close()


def test_missing_native_capability_logs_without_breaking_window(notifications, caplog):
    window = SimpleNamespace(native=SimpleNamespace(),
                             events=SimpleNamespace(before_show=Event()))
    binding = notifications.install_notification_permission(window, ORIGIN)
    window.events.before_show.emit()
    assert 'notification' in caplog.text.lower()
    binding.close()


def test_launcher_installs_permission_hook_before_webview_start_and_cleans_up(notifications, tmp_path):
    import launcher
    from webview.event import Event as WindowEvent
    window = Mock()
    window.events = SimpleNamespace(closing=WindowEvent(window, True))
    view = Mock()
    view.create_window.return_value = window
    service = Mock(url=ORIGIN)
    backend = Mock(app=Mock(), run_status='idle', run_thread=None)
    binding = Mock()
    order = []
    install = Mock(side_effect=lambda *args: (order.append('installed') or binding))
    view.start.side_effect = lambda **kwargs: order.append('started')
    with patch.object(tempfile, 'tempdir', None), \
            patch.dict(os.environ), \
            patch.dict(sys.modules, {'server': backend, 'webview': view}), \
            patch.object(launcher, 'configure_logging'), \
            patch.object(launcher, 'resolve_model_root', return_value=tmp_path), \
            patch.object(launcher, 'resolve_case_storage', return_value=(tmp_path / 'cases', 'test', None)), \
            patch.object(launcher, 'resolve_state_storage', return_value=(tmp_path / 'state', None)), \
            patch.object(launcher, 'diagnostics', return_value={'dependencies': {}}), \
            patch.object(launcher, 'register_system_routes'), \
            patch.object(launcher, 'wait_until_ready'), \
            patch.object(launcher, 'LocalService', return_value=service), \
            patch.object(notifications, 'install_notification_permission', install):
        assert launcher.main(['--desktop']) == 0
    assert order == ['installed', 'started']
    install.assert_called_once_with(window, ORIGIN)
    binding.release.assert_called_once()

