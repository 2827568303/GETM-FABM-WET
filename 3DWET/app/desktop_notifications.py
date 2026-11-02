"""Window-scoped WebView2 notification permission handling.

The host supplies notification permission UI; WebView2 has no default prompt.
All native callbacks and deferral completion run on the owning WinForms thread.
"""
from __future__ import annotations

import logging
from types import SimpleNamespace
from urllib.parse import urlsplit


logger = logging.getLogger(__name__)


def _local_origin(uri):
    if not isinstance(uri, str) or not uri or '\\' in uri:
        return None
    if any(ord(character) < 33 or ord(character) == 127 for character in uri):
        return None
    try:
        parsed = urlsplit(uri)
        port = parsed.port
        if (parsed.scheme != 'http' or parsed.hostname != '127.0.0.1'
                or parsed.username is not None or parsed.password is not None
                or port is None or not 1 <= port <= 65535):
            return None
        return f'http://127.0.0.1:{port}'
    except (ValueError, TypeError):
        return None


class NotificationPermissionController:
    """Handle only Notifications, with one explicit choice per window session."""

    def __init__(self, origin, *, current_uri, prompt, schedule,
                 notification_kind, allow_state, deny_state):
        self.origin = _local_origin(origin)
        if self.origin is None:
            raise ValueError('Notification permission requires an explicit local service origin.')
        self.current_uri = current_uri
        self.prompt = prompt
        self.schedule = schedule
        self.notification_kind = notification_kind
        self.allow_state = allow_state
        self.deny_state = deny_state
        self.choice = None
        self.closed = False
        self.pending = []
        self.prompt_pending = False

    def _at_service(self):
        return not self.closed and _local_origin(self.current_uri()) == self.origin

    def requested(self, sender, args):
        if args.PermissionKind != self.notification_kind:
            return
        try:
            # Fail closed before anything that can fail or start a nested UI loop.
            args.State = self.deny_state
            args.SavesInProfile = False
            args.Handled = True
            if _local_origin(args.Uri) != self.origin or not self._at_service():
                return
            if self.choice is not None:
                args.State = self.allow_state if self.choice else self.deny_state
                return
            deferral = args.GetDeferral()
            self.pending.append((args, deferral))
            if not self.prompt_pending:
                self.prompt_pending = True
                # A modal dialog inside PermissionRequested would violate WebView2
                # reentrancy rules. Post it after this event returns instead.
                self.schedule(self._resolve)
        except Exception:
            logger.exception('Desktop notification permission request failed; permission denied')
            self._finish_pending(False)

    def _resolve(self):
        if not self.pending:
            return
        allowed = False
        try:
            if self._at_service():
                answer = self.prompt(self.origin)
                if self._at_service():
                    allowed = answer is True
                    if answer is True or answer is False:
                        self.choice = answer
                    logger.info('Desktop notification permission %s for %s (window session only)',
                                'allowed' if allowed else 'denied', self.origin)
        except Exception:
            logger.exception('Desktop notification permission dialog failed; permission denied')
        finally:
            self._finish_pending(allowed and not self.closed)

    def _finish_pending(self, allowed):
        pending, self.pending = self.pending, []
        self.prompt_pending = False
        for args, deferral in pending:
            try:
                args.State = self.allow_state if allowed else self.deny_state
            except Exception:
                logger.exception('Could not set desktop notification permission result')
            finally:
                try:
                    deferral.Complete()
                except Exception:
                    logger.exception('Could not complete desktop notification permission deferral')

    def close(self):
        self.closed = True
        self.choice = None
        self._finish_pending(False)


def _load_webview2():
    """Import only after pywebview has created its WinForms/WebView2 backend."""
    from Microsoft.Web.WebView2.Core import (CoreWebView2PermissionKind,
                                            CoreWebView2PermissionState)
    from System import Action
    from System.Windows.Forms import (DialogResult, MessageBox, MessageBoxButtons,
                                      MessageBoxDefaultButton, MessageBoxIcon)

    def confirm(owner, origin):
        message = ('允许 3DWET Studio 显示模型运行进度提醒、完成或失败通知吗？\n'
                   'Allow 3DWET Studio to show model run progress reminders, completion or failure notifications?\n\n'
                   f'来源 / Origin: {origin}\n\n'
                   '仅在本窗口会话中记住选择。\n'
                   'Your choice applies only to this window session.')
        result = MessageBox.Show(owner, message, '3DWET Studio · 通知 / Notifications',
                                 MessageBoxButtons.YesNo, MessageBoxIcon.Question,
                                 MessageBoxDefaultButton.Button2)
        return result == DialogResult.Yes

    return SimpleNamespace(notification_kind=CoreWebView2PermissionKind.Notifications,
                           allow_state=CoreWebView2PermissionState.Allow,
                           deny_state=CoreWebView2PermissionState.Deny,
                           action=Action, confirm=confirm)


class _WindowNotificationBinding:
    def __init__(self, window, origin):
        self.window = window
        self.origin = origin
        self.control = None
        self.core = None
        self.api = None
        self.policy = None
        self.closed = False
        self.subscriptions = []
        self._subscribe(window.events, 'before_show', self._before_show)

    def _subscribe(self, owner, name, handler):
        event = getattr(owner, name)
        event += handler
        self.subscriptions.append((owner, name, handler))

    def _before_show(self):
        if self.closed or self.control is not None:
            return
        try:
            # pywebview's synchronous before_show runs on its WinForms UI thread
            # after native.webview exists and before the first message pump.
            self.control = self.window.native.webview
            self.api = _load_webview2()
            self._subscribe(self.window.native, 'FormClosed', self._disposed)
            self._subscribe(self.control, 'Disposed', self._disposed)
            self._subscribe(self.control, 'CoreWebView2InitializationCompleted', self._initialized)
            if self.control.CoreWebView2 is not None:
                self._attach(self.control.CoreWebView2)
        except Exception:
            logger.exception('Could not attach desktop notification permission handling; page notices remain available')

    def _initialized(self, sender, args):
        if self.closed:
            return
        try:
            if not args.IsSuccess:
                logger.error('Desktop notification permissions unavailable: WebView2 initialization failed: %s',
                             args.InitializationException)
                return
            self._attach(sender.CoreWebView2)
        except Exception:
            logger.exception('Could not initialize desktop notification permission handling')

    def _attach(self, core):
        if self.closed or self.core is not None:
            return
        policy = NotificationPermissionController(
            self.origin, current_uri=lambda: str(core.Source),
            prompt=lambda origin: self.api.confirm(self.window.native, origin),
            schedule=lambda callback: self.control.BeginInvoke(self.api.action(callback)),
            notification_kind=self.api.notification_kind, allow_state=self.api.allow_state,
            deny_state=self.api.deny_state)
        self._subscribe(core, 'PermissionRequested', policy.requested)
        self.core, self.policy = core, policy
        logger.info('Desktop notification permission handling attached for %s', policy.origin)

    def _disposed(self, sender, args):
        self.close()

    def close(self):
        """Native teardown, called only by the owning STA's lifecycle events."""
        if self.closed:
            return
        self.closed = True
        if self.policy is not None:
            self.policy.close()
        for owner, name, handler in reversed(self.subscriptions):
            try:
                event = getattr(owner, name)
                event -= handler
            except Exception:
                logger.exception('Could not detach desktop notification permission handler')
        self.subscriptions.clear()

    def release(self):
        """After webview.start returns, release Python state without native calls.

        pywebview joins its separate STA before returning to the Python main
        thread. Native teardown must already have run on FormClosed/Disposed;
        exceptional startup/exit paths must not access COM on this thread.
        """
        if self.closed:
            return
        self.closed = True
        if self.policy is not None:
            if self.policy.pending:
                logger.warning('Desktop notification UI ended before pending permission cleanup')
            self.policy.closed = True
            self.policy.choice = None
            self.policy.pending.clear()
            self.policy.prompt_pending = False
        for owner, name, handler in self.subscriptions:
            if owner is self.window.events:
                event = getattr(owner, name)
                event -= handler
        self.subscriptions.clear()
        self.control = self.core = self.api = None


def install_notification_permission(window, origin):
    """Register a window-local hook without affecting web launches or other permissions."""
    try:
        return _WindowNotificationBinding(window, origin)
    except Exception:
        logger.exception('Desktop notification permission hook unavailable; page notices remain available')
        return None
