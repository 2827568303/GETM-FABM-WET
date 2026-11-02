const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const source = fs.readFileSync('3DWET/app/static/js/app.js', 'utf8');
const template = fs.readFileSync('3DWET/app/templates/index.html', 'utf8');
const english = JSON.parse(fs.readFileSync('3DWET/app/static/i18n/en.json', 'utf8'));
assert.match(template, /id="run-notification-enable"[^>]*onclick="enableRunNotifications\(\)"/,
  'the notification center must provide an explicit user-activated opt-in');
assert.equal(english.messages['启用桌面通知'], 'Enable desktop notifications',
  'the accessible opt-in label must be available in English');

function extractFunction(name) {
  const start = source.indexOf(`function ${name}(`);
  assert.ok(start >= 0, `${name} must exist`);
  const declarationStart = source.slice(Math.max(0, start - 6), start) === 'async ' ? start - 6 : start;
  const open = source.indexOf('{', start);
  let depth = 0;
  for (let i = open; i < source.length; i++) {
    if (source[i] === '{') depth++;
    if (source[i] === '}' && --depth === 0) return source.slice(declarationStart, i + 1);
  }
  throw new Error(`Could not extract ${name}`);
}

const elements = new Map();
const element = id => {
  if (!elements.has(id)) elements.set(id, {disabled: false, hidden: false, textContent: ''});
  return elements.get(id);
};
let permissionRequests = 0;
const notifications = {permission: 'default', requestPermission: async () => {
  permissionRequests++;
  notifications.permission = 'granted';
  return notifications.permission;
}};
const toasts = [];
const context = vm.createContext({
  state: {activeCase: '/synthetic', runPollTimer: null},
  window: {Notification: notifications, StudioI18n: {locale: () => 'en-US'}},
  Notification: notifications,
  $: element,
  document: {getElementById: element},
  api: async () => ({success: true}),
  advanceOutputRevision() {},
  toast: (...args) => toasts.push(args),
  updateRunNotificationStatus() {},
  clearInterval() {},
  setInterval: () => 1,
  pollRunStatus() {},
});
vm.runInContext(extractFunction('startRun'), context);
vm.runInContext(extractFunction('enableRunNotifications'), context);

(async () => {
  await context.startRun();
  assert.equal(permissionRequests, 0, 'starting a normal model run must never request notification permission');
  assert.equal(element('run-notification-center').hidden, false, 'the in-app run status remains available');

  await context.enableRunNotifications();
  assert.equal(permissionRequests, 1, 'only the explicit opt-in action requests permission');
  assert.equal(notifications.permission, 'granted');
  console.log('run notification opt-in: no prompt on run start; explicit opt-in requests permission PASS');
})().catch(error => { console.error(error); process.exitCode = 1; });
