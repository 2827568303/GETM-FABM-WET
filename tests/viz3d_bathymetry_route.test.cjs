const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const test = require('node:test');

const source = fs.readFileSync('3DWET/app/static/js/app.js', 'utf8');
const workspaceSource = fs.readFileSync('3DWET/app/static/js/scientific_workspace.js', 'utf8');
const viz3dSource = fs.readFileSync('3DWET/app/static/js/viz3d.js', 'utf8');

function functionSource(name) {
  const start = source.indexOf(`async function ${name}(`);
  assert.notEqual(start, -1, `missing ${name}`);
  const open = source.indexOf('{', start);
  let depth = 0;
  for (let i = open; i < source.length; i++) {
    if (source[i] === '{') depth++;
    if (source[i] === '}' && --depth === 0) return source.slice(start, i + 1);
  }
  throw new Error(`unterminated ${name}`);
}

function nestedFunctionSource(sourceText, name) {
  const start = sourceText.indexOf(`function ${name}(`);
  assert.notEqual(start, -1, `missing ${name}`);
  const open = sourceText.indexOf('{', start);
  let depth = 0;
  for (let i = open; i < sourceText.length; i++) {
    if (sourceText[i] === '{') depth++;
    if (sourceText[i] === '}' && --depth === 0) return sourceText.slice(start, i + 1);
  }
  throw new Error(`unterminated ${name}`);
}

function namedFunctionSource(sourceText, name) {
  const start = sourceText.indexOf(`function ${name}(`);
  assert.notEqual(start, -1, `missing ${name}`);
  const open = sourceText.indexOf('{', start);
  let depth = 0;
  for (let i = open; i < sourceText.length; i++) {
    if (sourceText[i] === '{') depth++;
    if (sourceText[i] === '}' && --depth === 0) return sourceText.slice(start, i + 1);
  }
  throw new Error(`unterminated ${name}`);
}

function loadUpdate(options) {
  const calls = { bathymetry: [], waterbody: [], surface2d: [] };
  const controls = {
    'viz3d-iso-var': { value: options.variable },
    'viz3d-iso-time': { value: '2' },
    'viz3d-iso-ve': { value: '1' },
    'viz3d-opacity': { value: '0.8' },
    'viz3d-mesh-mode': { value: 'triangles' },
    'viz3d-line-density': { value: '1' },
    'viz3d-line-opacity': { value: '.3' },
    'viz3d-mesh-nodes': { checked: false },
    'viz3d-show-land': { checked: true },
    'viz3d-iso-render': { value: options.render || 'waterbody' },
    'viz3d-iso-overlay': { checked: true },
    'viz3d-iso-quality': { value: '96' },
    'viz3d-iso-level': { value: '0' },
    'viz3d-iso-layer': { value: '-1' },
    'viz3d-iso-stack': { checked: false },
  };
  const context = {
    hasVerticalResultDimension: (variable) => variable?.ndim === 4 || (Array.isArray(variable?.dims) && variable.dims.includes('sigma')),
    state: { activeCasePath: 'test-lake', variables3d: [], variables2d: [], timeLabels3d: [], caseRevision: 1 },
    window: {
      invalidateScientific3D() {},
      setSpatialSectionPlaybackStatus: (...args) => { calls.sectionStatus = args; },
      ScientificWorkspace: {
        syncFrom() {},
        isPlaying: () => options.playing === true,
        variableMetadata: (name) => name === options.variable ? { name, ndim: options.ndim, nlev: 4 } : null,
        dateLabel: () => 'time-2',
        current: () => options.main || null,
        failure() {},
      },
    },
    ModelDates: { format: () => '' },
    document: {
      getElementById: () => ({ textContent: '' }),
      querySelector: () => options.sectionOpen ? { open: true } : null,
    },
    $: (id) => controls[id.replace(/^#/, '')] || null,
    toast() {},
    renderBathymetry3D: async (args) => calls.bathymetry.push(args),
    render3DWaterBody: async (name, time, args) => calls.waterbody.push({ name, time, args }),
    render2DAs3DSurface: async (name, time, level, args) => calls.surface2d.push({ name, time, level, args }),
    updateSpatialSection: async () => { calls.section = (calls.section || 0) + 1; },
  };
  vm.runInNewContext(functionSource('updateViz3dIso'), context);
  return { update: context.updateViz3dIso, calls };
}

test('3D D routes to static bathymetry even when the waterbody overlay is checked', async () => {
  const { update, calls } = loadUpdate({ variable: 'D', ndim: 3 });
  await update();
  assert.equal(calls.bathymetry.length, 1, '2D depth must hand rendering to the static lake-basin bathymetry path');
  assert.equal(calls.waterbody.length, 0, '2D depth must not enter the true-4D waterbody renderer');
});

test('explicit variable-height surface keeps rendering D values', async () => {
  const { update, calls } = loadUpdate({ variable: 'D', ndim: 3, render: 'surface2d' });
  await update();
  assert.equal(calls.bathymetry.length, 0);
  assert.equal(calls.surface2d.length, 1);
  assert.equal(calls.surface2d[0].name, 'D');
});

test('true 4D waterbody variables retain the selected overlay', async () => {
  const { update, calls } = loadUpdate({ variable: 'temperature', ndim: 4 });
  await update();
  assert.equal(calls.bathymetry.length, 0);
  assert.equal(calls.waterbody.length, 1);
  assert.equal(calls.waterbody[0].args.overlay, true);
});

test('3D playback skips the expensive section redraw and labels its last completed frame', async () => {
  const main = { variable: 'temperature', time: 2 };
  const { update, calls } = loadUpdate({ variable: 'temperature', ndim: 4, playing: true, sectionOpen: true, main });
  await update();
  assert.equal(calls.section || 0, 0);
  assert.deepEqual(calls.sectionStatus, [2, 'time-2']);
});

test('a stopped 3D refresh updates the open section to the current frame', async () => {
  const main = { variable: 'temperature', time: 2 };
  const { update, calls } = loadUpdate({ variable: 'temperature', ndim: 4, playing: false, sectionOpen: true, main });
  await update();
  assert.equal(calls.section, 1);
  assert.equal(calls.sectionStatus, undefined);
});

test('stopping playback refreshes an open section once at the final displayed frame', () => {
  let sectionRefreshes = 0;
  const button = { textContent: '', replaceChildren() {}, setAttribute() {} };
  const records = new Map([['viz3d', { timer: 12, playing: true, resume: false, playGeneration: 2, busy: 0 }]]);
  const context = {
    root: { StudioIcons: { node: (name) => ({ name }) }, updateSpatialSection: () => { sectionRefreshes++; } },
    records,
    record(kind) { return records.get(kind); },
    $: () => button,
    clearTimeout() {},
    tr: (_zh, en) => en,
    activePage: 'viz3d',
    document: { querySelector: () => ({ open: true }) },
  };
  vm.runInNewContext(`${nestedFunctionSource(workspaceSource, 'refreshStoppedSpatialSection')}\n${nestedFunctionSource(workspaceSource, 'stop')}`, context);
  context.stop('viz3d', true);
  assert.equal(sectionRefreshes, 1);
  assert.equal(context.record('viz3d').playing, false);
});

test('pause during an in-flight main render leaves final section refresh to that render', () => {
  let sectionRefreshes = 0;
  const button = { textContent: '', replaceChildren() {}, setAttribute() {} };
  const records = new Map([['viz3d', { timer: 12, playing: true, resume: false, playGeneration: 2, busy: 1 }]]);
  const context = {
    root: { StudioIcons: { node: (name) => ({ name }) }, updateSpatialSection: () => { sectionRefreshes++; } }, records,
    record(kind) { return records.get(kind); }, $: () => button, clearTimeout() {},
    tr: (_zh, en) => en, activePage: 'viz3d',
    document: { querySelector: () => ({ open: true }) },
  };
  vm.runInNewContext(`${nestedFunctionSource(workspaceSource, 'refreshStoppedSpatialSection')}\n${nestedFunctionSource(workspaceSource, 'stop')}`, context);
  context.stop('viz3d', true);
  assert.equal(sectionRefreshes, 0);
});

test('playback section status names the retained section time and cancels a stale request', () => {
  const status = { textContent: '', dataset: {} };
  const container = {
    _viz3dLastPlot: { timeLabel: '帧 6 · 2020-01-02 00:00:00' },
    _viz3dStatusElement: status,
    dataset: {},
  };
  const appState = { spatialSectionRequest: 9 };
  const context = {
    window: { state: appState, StudioI18n: { scientificText: (zh) => zh } },
    document: { getElementById: () => container },
  };
  vm.runInNewContext(`let _spatialSectionToken=3;\n${namedFunctionSource(viz3dSource, 'setSpatialSectionPlaybackStatus')}\nthis.testToken=()=>_spatialSectionToken;`, context);
  context.setSpatialSectionPlaybackStatus(7, '帧 7 · 2020-01-02 01:00:00');
  assert.match(status.textContent, /播放中暂停剖面刷新/);
  assert.match(status.textContent, /帧 6/);
  assert.match(status.textContent, /帧 7/);
  assert.equal(context.testToken(), 4);
  assert.equal(appState.spatialSectionRequest, 10);
});
