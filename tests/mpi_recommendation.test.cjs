const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const appSource = fs.readFileSync('3DWET/app/static/js/app.js', 'utf8');
const template = fs.readFileSync('3DWET/app/templates/index.html', 'utf8');
const loadDeclaration = appSource.match(/async function loadMpiRunCapabilities\(\)\s*\{[\s\S]*?\n\}/);
const detectDeclaration = appSource.match(/async function detectAndApplyMpiRecommendation\(\)\s*\{[\s\S]*?\n\}/);

function setup({responses} = {}) {
  const casePath = 'D:/case-a';
  const elements = {
    'mpi-run-control': {},
    'mpi-run-enabled': {checked: false, disabled: true, onchange: null},
    'mpi-process-count': {value: '8', disabled: true, options: [], onchange: null,
      replaceChildren(...options) { this.options = options; }},
    'mpi-run-capability': {textContent: ''},
    'mpi-detect-recommendation': {disabled: true, onclick: null},
  };
  const state = {casePath, activeCasePath: casePath, caseType: 'getm', storageReadOnly: false,
    caseRevision: 1, mpiCapabilitiesRequest: 0, mpiRecommendationRequest: 0,
    mpiSelectionByCase: new Map(), mpiProcessCountByCase: new Map([[casePath, 8]])};
  const queue = [...(responses || [])];
  const context = {state, Map, Number, String, Array, Set, Math,
    document: {getElementById: id => elements[id], createElement: tag => ({tagName: tag.toUpperCase(), value: '', textContent: ''})},
    api: async () => {
      const next = queue.shift();
      if (next instanceof Error) throw next;
      return await next;
    }};
  assert.ok(loadDeclaration, 'loadMpiRunCapabilities should exist');
  vm.runInNewContext(loadDeclaration[0] + '\nthis.load=loadMpiRunCapabilities;', context);
  if (detectDeclaration) {
    vm.runInNewContext(detectDeclaration[0] + '\nthis.detect=detectAndApplyMpiRecommendation;', context);
  }
  return {state, elements, load: context.load, detect: context.detect};
}

const caps = (max, recommended, allowed) => ({enabled: true, max_processes: max,
  recommended_processes: recommended, allowed_processes: allowed, reason: ''});

test('button re-detects affinity and grid limits, then applies the recommended valid count', async () => {
  const {state, elements, load, detect} = setup({responses: [
    caps(8, 4, [1, 2, 4, 8]),
    caps(32, 16, [1, 2, 4, 8, 12, 16, 32]),
  ]});
  await load();
  assert.ok(detect, 'detectAndApplyMpiRecommendation should exist');
  assert.equal(elements['mpi-process-count'].value, '8', 'manual case preference is preserved on load');
  elements['mpi-run-enabled'].checked = false;
  await detect();
  assert.equal(elements['mpi-process-count'].value, '16');
  assert.equal(state.mpiProcessCountByCase.get('D:/case-a'), 16);
  assert.equal(elements['mpi-run-enabled'].checked, false, 'adopting a count must not enable MPI implicitly');
  assert.match(elements['mpi-run-capability'].textContent, /可用逻辑处理器：32/);
  assert.match(elements['mpi-run-capability'].textContent, /已采用建议 16 个进程/);
  assert.doesNotMatch(elements['mpi-run-capability'].textContent, /允许进程数/);
  assert.match(elements['mpi-run-capability'].textContent, /不保证最快/);
});

test('failed detection keeps the manual process selection and exposes an actionable error', async () => {
  const {state, elements, load, detect} = setup({responses: [
    caps(8, 4, [1, 2, 4, 8]), new Error('capability probe unavailable'),
  ]});
  await load();
  assert.ok(detect, 'detectAndApplyMpiRecommendation should exist');
  elements['mpi-process-count'].value = '8';
  elements['mpi-process-count'].onchange();
  await detect();
  assert.equal(elements['mpi-process-count'].value, '8');
  assert.equal(state.mpiProcessCountByCase.get('D:/case-a'), 8);
  assert.match(elements['mpi-run-capability'].textContent, /capability probe unavailable/);
  assert.equal(elements['mpi-detect-recommendation'].disabled, false);
});

test('stale detection response cannot change the count after a case switch', async () => {
  let resolveProbe;
  const {state, elements, load, detect} = setup({responses: [
    caps(8, 4, [1, 2, 4, 8]), new Promise(resolve => { resolveProbe = resolve; }),
  ]});
  await load();
  assert.ok(detect, 'detectAndApplyMpiRecommendation should exist');
  const pending = detect();
  state.activeCasePath = 'D:/case-b';
  state.caseRevision++;
  resolveProbe(caps(32, 16, [1, 2, 4, 8, 16, 32]));
  await pending;
  assert.equal(elements['mpi-process-count'].value, '8');
  assert.equal(state.mpiProcessCountByCase.get('D:/case-a'), 8);
  assert.equal(state.mpiProcessCountByCase.has('D:/case-b'), false);
});

test('run controls expose a single-click recommendation action', () => {
  assert.match(template, /id="mpi-detect-recommendation"[^>]*onclick="detectAndApplyMpiRecommendation\(\)"/);
  assert.match(template, /检测并采用建议/);
});
