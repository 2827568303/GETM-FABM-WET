const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const source = fs.readFileSync('3DWET/app/static/js/app.js', 'utf8');

function extractFunction(name) {
  const start = source.indexOf(`function ${name}(`);
  assert.ok(start >= 0, `${name} must exist`);
  const declarationStart = source.slice(Math.max(0, start - 6), start) === 'async ' ? start - 6 : start;
  const signatureEnd = source.indexOf(') {', start);
  const open = source.indexOf('{', signatureEnd);
  let depth = 0;
  for (let i = open; i < source.length; i++) {
    if (source[i] === '{') depth++;
    if (source[i] === '}' && --depth === 0) return source.slice(declarationStart, i + 1);
  }
  throw new Error(`Could not extract ${name}`);
}

const elements = new Map();
const element = id => {
  if (!elements.has(id)) elements.set(id, {checked: false, disabled: false, textContent: '', style: {}, value: ''});
  return elements.get(id);
};
const requests = [];
class MockXhr {
  open(method, url) { this.method = method; this.url = url; }
  setRequestHeader() {}
  send(body) {
    requests.push({method: this.method, url: this.url, body});
    this.status = 400;
    this.responseText = JSON.stringify({success: false, error: 'test response'});
    this.onload();
  }
}

const context = vm.createContext({
  state: {
    activeCase: 'isolated-case',
    activeCasePath: 'E:\\isolated-case',
    caseType: 'getm',
    storageReadOnly: false,
    caseRevision: 1,
    mpiRecommendationRequest: 0,
    mpiProcessCountByCase: new Map(),
    runPollTimer: null,
  },
  window: {performance: {now: () => 0}, StudioI18n: {locale: () => 'en-US'}},
  document: {getElementById: element},
  XMLHttpRequest: MockXhr,
  $: element,
  confirmStudio: async () => true,
  toast() {},
  loadOutputConfig() {},
  setTimeout,
  clearInterval() {},
  setInterval: () => 1,
  pollRunStatus() {},
  advanceOutputRevision() {},
  api: null,
});
element('output-time-unit').value = 'hour';
element('output-time-step').value = '3600';
element('output-sync-interval').value = '1';
element('mpi-run-enabled').disabled = false;
element('mpi-process-count').disabled = false;
element('mpi-run-capability').textContent = '';
element('mpi-detect-recommendation').disabled = false;
vm.runInContext(extractFunction('api'), context);
vm.runInContext(extractFunction('startRun'), context);
vm.runInContext(extractFunction('fixSyncInterval'), context);
vm.runInContext(extractFunction('saveOutputConfig'), context);
vm.runInContext(extractFunction('startMpiTuning'), context);

(async () => {
  const assertJsonObject = (index, expected, label) => {
    const request = requests[index];
    assert.ok(request, `${label} must send a request`);
    assert.equal(request.method, 'POST');
    const parsed = JSON.parse(request.body);
    assert.equal(typeof parsed, 'object', `${label} must send one JSON object, not a JSON-encoded string`);
    assert.deepEqual(JSON.parse(JSON.stringify(parsed)), expected);
  };

  await context.startRun();
  assertJsonObject(0, {
    cores: 1,
    parallel_mode: 'auto',
    compress_results: false,
    mpi: false,
    processes: 1,
  }, 'run start');

  await context.fixSyncInterval();
  assertJsonObject(1, {sync_interval: 1}, 'sync interval repair');

  await context.saveOutputConfig();
  assertJsonObject(2, {time_unit: 'hour', time_step: 3600, sync_interval: 1}, 'output configuration save');

  await context.startMpiTuning();
  assertJsonObject(3, {duration_seconds: 10800, repetitions: 2}, 'MPI tuning start');
  console.log('run and output controls send single JSON objects through the shared API helper PASS');
})().catch(error => { console.error(error); process.exitCode = 1; });
