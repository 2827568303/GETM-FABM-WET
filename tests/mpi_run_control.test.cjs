const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const source = fs.readFileSync('3DWET/app/static/js/app.js', 'utf8');
const declaration = source.match(/async function loadMpiRunCapabilities\(\)\s*\{[\s\S]*?\n\}/);
assert.ok(declaration, 'loadMpiRunCapabilities should exist');
const runSummaryDeclaration = source.match(/function runStepSummary\(status\)\s*\{[\s\S]*?\n\}/);
const etaTextDeclaration = source.match(/function runEtaText\(status, english = window\.StudioI18n\?\.locale\?\.\(\) === 'en-US'\)\s*\{[\s\S]*?\n\}/);

function setup({casePath = 'D:/case-a', caseType = 'getm', storageReadOnly = false,
                capabilities = {enabled: true, max_processes: 32, recommended_processes: 16,
                  allowed_processes: Array.from({length: 32}, (_, index) => index + 1)},
                api} = {}) {
  const elements = {
    'mpi-run-control': {},
    'mpi-run-enabled': {checked: false, disabled: true, onchange: null},
    'mpi-process-count': {value: '16', disabled: true, options: [], onchange: null,
      replaceChildren(...options) { this.options = options; }},
    'mpi-detect-recommendation': {disabled: true, onclick: null},
    'mpi-run-capability': {textContent: ''},
  };
  const state = {casePath, activeCasePath: casePath, caseType, storageReadOnly,
    caseRevision: 1, mpiCapabilitiesRequest: 0, mpiRecommendationRequest: 0,
    mpiSelectionByCase: new Map(), mpiProcessCountByCase: new Map()};
  const context = {state, Map, document: {
      getElementById: id => elements[id],
      createElement: tag => ({tagName: tag.toUpperCase(), value: '', textContent: ''}),
    },
    api: api || (async () => capabilities)};
  vm.runInNewContext(declaration[0] + '\nthis.loadMpiRunCapabilities=loadMpiRunCapabilities;', context);
  return {state, elements, load: context.loadMpiRunCapabilities};
}

test('available writable GETM defaults to recommended MPI and remembers user opt-out', async () => {
  const {state, elements, load} = setup();
  await load();
  const toggle = elements['mpi-run-enabled'];
  const count = elements['mpi-process-count'];
  assert.equal(toggle.disabled, false);
  assert.equal(toggle.checked, true);
  assert.equal(count.value, '16');
  assert.equal(count.options.length, 32);
  assert.equal(count.options[0].value, '1');
  assert.equal(count.options.at(-1).value, '32');
  assert.equal(count.disabled, false);

  toggle.checked = false;
  toggle.onchange();
  assert.equal(count.disabled, true);
  assert.equal(state.mpiSelectionByCase.get('D:/case-a'), false);
  await load();
  assert.equal(toggle.checked, false);
});

test('case changes reset to the safe case-specific default and disable MPI for GOTM/read-only cases', async () => {
  const {state, elements, load} = setup();
  await load();
  elements['mpi-run-enabled'].checked = false;
  elements['mpi-run-enabled'].onchange();

  state.activeCasePath = 'D:/column';
  state.caseType = 'gotm_read_only';
  state.caseRevision++;
  await load();
  assert.equal(elements['mpi-run-enabled'].checked, false);
  assert.equal(elements['mpi-run-enabled'].disabled, true);
  assert.equal(elements['mpi-process-count'].disabled, true);

  state.activeCasePath = 'D:/case-b';
  state.caseType = 'getm';
  state.caseRevision++;
  await load();
  assert.equal(elements['mpi-run-enabled'].checked, true);
  assert.equal(elements['mpi-run-enabled'].disabled, false);

  state.activeCasePath = 'D:/case-a';
  state.caseRevision++;
  await load();
  assert.equal(elements['mpi-run-enabled'].checked, false);
});

test('unavailable capabilities keep the MPI controls disabled and unchecked', async () => {
  const {elements, load} = setup({capabilities: {
    enabled: false, max_processes: 32, recommended_processes: 16,
    reason: 'Unavailable: MPI launcher',
  }});
  await load();
  assert.equal(elements['mpi-run-enabled'].checked, false);
  assert.equal(elements['mpi-run-enabled'].disabled, true);
  assert.equal(elements['mpi-process-count'].disabled, true);
  assert.match(elements['mpi-run-capability'].textContent, /MPI launcher/);
});

test('initial page load without a case stays disabled, then enables MPI after GETM restore', async () => {
  const {state, elements, load} = setup({casePath: null, caseType: null});
  await load();
  assert.equal(elements['mpi-run-enabled'].checked, false);
  assert.equal(elements['mpi-run-enabled'].disabled, true);

  state.activeCasePath = 'D:/restored-case';
  state.caseType = 'getm';
  state.caseRevision++;
  await load();
  assert.equal(elements['mpi-run-enabled'].checked, true);
  assert.equal(elements['mpi-run-enabled'].disabled, false);
});

test('stale capability response cannot re-enable MPI after a case switch', async () => {
  const pending = [];
  const {state, elements, load} = setup({api: () => new Promise(resolve => pending.push(resolve))});
  const first = load();
  state.activeCasePath = 'D:/column';
  state.caseType = 'gotm_read_only';
  state.caseRevision++;
  const second = load();
  pending[1]({enabled: true, max_processes: 32, recommended_processes: 16});
  await second;
  pending[0]({enabled: true, max_processes: 32, recommended_processes: 16});
  await first;
  assert.equal(elements['mpi-run-enabled'].checked, false);
  assert.equal(elements['mpi-run-enabled'].disabled, true);
});

test('rank selector exposes only exact grid-safe MPI decompositions', async () => {
  const allowed = [1, 2, 4, 8, 12, 16];
  const {elements, load} = setup({capabilities: {
    enabled: true, max_processes: 32, recommended_processes: 16,
    allowed_processes: allowed,
  }});
  await load();
  assert.deepEqual(elements['mpi-process-count'].options.map(option => Number(option.value)), allowed);
  assert.equal(elements['mpi-process-count'].value, '16');
  assert.equal(elements['mpi-run-capability'].textContent,
    '当前进程可用逻辑处理器：32；建议 16 个进程。建议值不保证最快。');
  assert.doesNotMatch(elements['mpi-run-capability'].textContent, /当前网格\/halo 可选/);
  assert.equal(elements['mpi-detect-recommendation'].disabled, false);
});

test('merge phase replaces solver ETA with a clear phase label and retains rank count', () => {
  assert.ok(runSummaryDeclaration, 'runStepSummary should exist');
  assert.ok(etaTextDeclaration, 'runEtaText should exist');
  const context = {window: {StudioI18n: {locale: () => 'zh-CN'}}, fmt: value => String(value)};
  vm.runInNewContext(runSummaryDeclaration[0] + '\n' + etaTextDeclaration[0]
    + '\nthis.summary=runStepSummary;this.etaText=runEtaText;', context);
  const status = {status: 'running', phase: 'merging', current_step: 3400, total_steps: 3456,
    performance: {solver_mode: 'MPI (4 ranks)'}};
  assert.match(context.summary(status), /正在合并输出/);
  assert.match(context.summary(status), /MPI \(4 ranks\)/);
  assert.equal(context.etaText(status), '合并输出中');

  const english = {window: {StudioI18n: {locale: () => 'en-US'}}, fmt: value => String(value)};
  vm.runInNewContext(etaTextDeclaration[0] + '\nthis.etaText=runEtaText;', english);
  assert.equal(english.etaText(status), 'Merging outputs');
});
