const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const source = fs.readFileSync('3DWET/app/static/js/app.js', 'utf8');
const template = fs.readFileSync('3DWET/app/templates/index.html', 'utf8');
const english = JSON.parse(fs.readFileSync('3DWET/app/static/i18n/en.json', 'utf8'));

assert.match(template, /id="run-console-load-more"[^>]*aria-controls="run-log"/,
  'older run log lines must have a labeled control linked to the log region');
assert.match(template, /id="run-console-copy"[^>]*aria-controls="run-log"/,
  'the copy action must be linked to the log region');
assert.match(template, /id="run-log"[^>]*role="log"[^>]*tabindex="0"/,
  'the console must be keyboard reachable and exposed as a log region');
for (const label of ['加载更早日志', '复制已加载日志', '日志来源：当前案例目录中的 model_run.log。此处由应用读取日志文件展示，不是原生命令提示符。', '已加载最近 {count} 行日志；已到当前保留范围上限。完整日志仍保存在 model_run.log。']) {
  assert.ok(english.messages[label], `English localization must exist for: ${label}`);
}

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

class MockElement {
  constructor(text = '') {
    this.textContent = text;
    this.children = [];
    this.scrollHeight = 100;
    this.scrollTop = 0;
    this.clientHeight = 100;
  }
  appendChild(child) { this.children.push(child); this.scrollHeight += 10; }
  get firstChild() { return this.children[0] || null; }
  insertBefore(child, before) {
    const index = before ? this.children.indexOf(before) : -1;
    this.children.splice(index < 0 ? this.children.length : index, 0, child);
    this.scrollHeight += 10;
  }
  removeChild(child) {
    this.children.splice(this.children.indexOf(child), 1);
    this.scrollHeight -= 10;
  }
  replaceChildren(...children) {
    this.children = children;
    this.scrollHeight = 100 + children.length * 10;
  }
}

const created = [];
const document = {createElement: () => {
  const node = {className: '', textContent: '', parentNode: null};
  created.push(node);
  return node;
}};
const context = vm.createContext({document, ModelDates: {formatText: value => value}});
vm.runInContext(extractFunction('appendRunLogLines'), context);
const runLogStatus = {textContent: ''};
context.$ = id => id === 'run-console-log-status' ? runLogStatus : null;
context.state = {runLogIdentity: 'run-1', runLogLimit: 500, lastLogSnapshot: 'old'};
vm.runInContext(extractFunction('syncRunLogContext'), context);
context.window = {StudioI18n: {locale: () => 'en-US'}};
context.fmt = (value, digits) => Number(value).toFixed(digits);
vm.runInContext(extractFunction('runStepSummary'), context);
vm.runInContext(extractFunction('runEtaText'), context);
assert.match(context.runStepSummary({status:'running',progress:null,current_step:null,total_steps:400,steps_per_second:null}), /Unknown.*Speed unknown/,
  'missing observations must be shown as unknown instead of fabricated zero values');
assert.equal(context.runEtaText({status:'running',eta_seconds:null,eta_minutes:null}), 'Unknown');
assert.match(context.runStepSummary({status:'running',phase:'compressing',current_step:10,total_steps:10,steps_per_second:2}), /Post-processing: compressing and verifying outputs/,
  'the step summary must identify post-solver compression explicitly');
assert.equal(context.runEtaText({status:'running',phase:'compressing',eta_seconds:1,eta_minutes:0.02}), 'Post-processing: compressing and verifying',
  'solver ETA must not be shown as output-compression ETA');

const log = new MockElement();
const cursor = {lastLines: []};
context.appendRunLogLines(log, ['start', 'step 1'], cursor);
assert.deepEqual(log.children.map(node => node.textContent), ['start', 'step 1']);
assert.equal(created.length, 2);
assert.equal(log.scrollTop, log.scrollHeight - log.clientHeight,
  'the initial render should follow the tail');

assert.equal(context.syncRunLogContext(log, 'run-1', cursor), false,
  'an empty poll for the same run must not clear loaded history');
assert.equal(log.children.length, 2);
assert.equal(context.syncRunLogContext(log, 'run-2', cursor), true,
  'a new run identity must clear stale rows even when its log array is empty');
assert.equal(log.children.length, 0);
assert.equal(cursor.lastLines.length, 0);
assert.equal(context.state.runLogLimit, 80);
context.appendRunLogLines(log, ['start', 'step 1'], cursor);

log.scrollTop = 0;
const beforeUpdate = [...log.children];
context.appendRunLogLines(log, ['start', 'step 1', 'step 2'], cursor);
assert.equal(log.children.length, 3, 'new lines should be appended');
assert.equal(log.children[0], beforeUpdate[0], 'existing rows must not be cleared and recreated');
assert.equal(log.scrollTop, 0, 'a user reading older lines must not be pulled back to the tail');

context.appendRunLogLines(log, ['old 1', 'old 2', 'start', 'step 1', 'step 2'], cursor);
assert.deepEqual(log.children.map(node => node.textContent), ['old 1', 'old 2', 'start', 'step 1', 'step 2'],
  'loading a larger window should prepend older lines in order');

context.appendRunLogLines(log, ['new run begins'], cursor);
assert.deepEqual(log.children.map(node => node.textContent), ['new run begins'],
  'a rotated log or new run with no shared tail should discard stale rows');

const copyElements = new Map([
  ['run-log', {querySelectorAll: () => [{textContent: 'line 1'}, {textContent: 'line 2'}]}],
  ['run-console-log-status', runLogStatus],
]);
const copyToasts = [];
let copiedText = '';
const copyContext = vm.createContext({
  $: id => copyElements.get(id),
  window: {StudioI18n: {t: value => value}},
  navigator: {clipboard: {writeText: async value => { copiedText = value; }}},
  toast: (...args) => copyToasts.push(args),
});
vm.runInContext(extractFunction('copyRunLogs'), copyContext);
(async () => {
  await copyContext.copyRunLogs();
  assert.equal(copiedText, 'line 1\nline 2', 'copy should include all currently loaded rows');
  assert.equal(copyElements.get('run-console-log-status').textContent, '运行日志已复制。');
  copyContext.navigator.clipboard.writeText = async () => { throw new Error('clipboard denied'); };
  await copyContext.copyRunLogs();
  assert.equal(copyElements.get('run-console-log-status').textContent, '无法访问剪贴板，请使用键盘选择日志并复制。');
  assert.equal(copyToasts.at(-1)[1], 'warning', 'clipboard failure should be announced without losing visible logs');
  console.log('run console controls, localization, incremental rendering, log reset, and copy paths PASS');
})().catch(error => { console.error(error); process.exitCode = 1; });
