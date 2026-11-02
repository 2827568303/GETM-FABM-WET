const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const test = require('node:test');

const source = fs.readFileSync('3DWET/app/static/js/viz3d.js', 'utf8');
const template = fs.readFileSync('3DWET/app/templates/index.html', 'utf8');

function functionSource(name) {
  const start = source.indexOf(`function ${name}(`);
  assert.notEqual(start, -1, `missing ${name}`);
  const open = source.indexOf(') {', start) + 2;
  let depth = 0;
  for (let i = open; i < source.length; i++) {
    if (source[i] === '{') depth++;
    if (source[i] === '}' && --depth === 0) return source.slice(start, i + 1);
  }
  throw new Error(`unterminated ${name}`);
}

function loadLakeTraces(featherTrace = () => null) {
  const context = {
    VIZ3D: { depthScale: [[0, '#75e3d7'], [1, '#173fbd']] },
    viz3dValidStyle: (style) => Number.isFinite(style?.min) && Number.isFinite(style?.max) && style.min <= style.max,
    viz3dValidStyle: (style) => Number.isFinite(style?.min) && Number.isFinite(style?.max) && style.min <= style.max,
    buildLakeContours: () => ({ x: [], y: [], z: [], depth: [] }),
    lakeDepthLevels: () => [],
    viz3dTicks: () => ({ values: [], labels: [] }),
    viz3dColorbar: (title, units) => ({ title: { text: `${title} (${units})` } }),
    viz3dHorizontalHover: () => '',
    smoothLakeShoreline: (x) => x,
    lakeLandTraces: () => [],
    lakeCoastalRimTrace: () => [],
    lakeStaticTraces: (geometry) => ({
      surface: { type: 'mesh3d', name: '水面', ...geometry.surface, meta: { waterbodyFrame: 'surface' } },
      shoreline: { type: 'scatter3d', name: '岸线', x: [], y: [], z: [] },
      land: [], wallMesh: geometry.walls, boundaryClipApplied: false,
    }),
    lakeShorelineFeatherTrace: featherTrace,
    lakeDisplayLines: () => [],
    viz3dSampledBoundary: () => false,
    lakeDisplayLines: (_mesh, _geometry, opts) => [{
      type: 'scatter3d', mode: 'lines', name: opts.meshMode,
      x: opts.meshMode === 'triangles' ? [0, 1, 0] : [0, 1],
      y: [0, 0, 1], z: [0, 0, 0], meta: { meshMode: opts.meshMode },
    }],
  };
  vm.runInNewContext(functionSource('lakeSurfaceDepthProjection'), context);
  // lakeTraces delegates shoreline ordering/feather insertion to a later-declared
  // production helper. Load that real dependency into this isolated VM context.
  vm.runInNewContext(functionSource('lakeRaiseShorelineTraces'), context);
  vm.runInNewContext(functionSource('lakeStaticWallPresentation'), context);
  vm.runInNewContext(functionSource('lakeTraces'), context);
  return context.lakeTraces;
}

function loadWaterbodyDiagnosticMode(search) {
  const context = { URLSearchParams };
  vm.runInNewContext(functionSource('viz3dWaterbodyDiagnosticMode'), context);
  return context.viz3dWaterbodyDiagnosticMode(search);
}

function filterWaterbodyDiagnosticTraces(traces, modes, overlay = true) {
  const context = {};
  vm.runInNewContext(functionSource('viz3dFilterWaterbodyDiagnosticTraces'), context);
  return context.viz3dFilterWaterbodyDiagnosticTraces(traces, modes, overlay);
}

test('waterbody diagnostic query accepts only explicit supported modes', () => {
  assert.deepEqual(Array.from(loadWaterbodyDiagnosticMode('')), []);
  assert.deepEqual(Array.from(loadWaterbodyDiagnosticMode('?viz3d-diagnostic=other')), []);
  assert.deepEqual(Array.from(loadWaterbodyDiagnosticMode('?viz3d-diagnostic=skip-wall')), ['skip-wall']);
  assert.deepEqual(Array.from(loadWaterbodyDiagnosticMode('?viz3d-diagnostic=skip-field')), ['skip-field']);
  assert.deepEqual(Array.from(loadWaterbodyDiagnosticMode('?viz3d-diagnostic=skip-bed')), ['skip-bed']);
  assert.deepEqual(Array.from(loadWaterbodyDiagnosticMode('?viz3d-diagnostic=force-bed')), ['force-bed']);
  assert.deepEqual(Array.from(loadWaterbodyDiagnosticMode('?viz3d-diagnostic=force-bed,skip-wall,skip-field,unknown')),
    ['force-bed', 'skip-wall', 'skip-field']);
  assert.deepEqual(Array.from(loadWaterbodyDiagnosticMode('?viz3d-diagnostic=bed-depth-colors')), ['bed-depth-colors']);
});

test('force-bed diagnostic restores only the dynamic bed above 80x and composes with other trace skips', () => {
  const render = loadLakeTraces();
  const geometry = {
    maxDepth: 12, ve: 166.5,
    floor: { x: [0, 1, 0], y: [0, 0, 1], z: [0, -3, -12], i: [0], j: [1], k: [2], intensity: [0, 3, 12] },
    surface: { x: [], y: [], z: [], i: [], j: [], k: [] },
    walls: { px: [0, 0, 1, 1], py: [0, 0, 0, 0], pz: [0, -3, 0, -3], i: [0, 0], j: [1, 3], k: [3, 2] },
    shoreline: { x: [], y: [], z: [] },
  };
  const baseline = render(geometry, false, {}, null, { staticBathymetry: false });
  const modes = loadWaterbodyDiagnosticMode('?viz3d-diagnostic=force-bed,skip-wall,skip-field');
  const diagnostic = render(geometry, false, {}, null, {
    staticBathymetry: false,
    forceBedTrace: modes.includes('force-bed'),
    showBedSurface: modes.includes('force-bed'),
    skipWallTrace: modes.includes('skip-wall'),
  });
  assert.ok(!baseline.some((trace) => trace.meta?.waterbodyFrame === 'bed'));
  const bed = diagnostic.find((trace) => trace.meta?.waterbodyFrame === 'bed');
  assert.ok(bed, 'force-bed must restore the same neutral dynamic bed fill above 80x');
  assert.equal(bed.color, undefined, 'neutral beds must avoid Plotly mesh3d direct-color encoding');
  assert.deepEqual(JSON.parse(JSON.stringify(bed.colorscale)), [[0, '#c5cdd1'], [1, '#c5cdd1']]);
  assert.equal(bed.intensitymode, 'vertex');
  assert.deepEqual(Array.from(bed.intensity), geometry.floor.intensity,
    'neutral style keeps the same depth intensity data as the bed geometry');
  assert.deepEqual(Array.from(bed.x), geometry.floor.x);
  assert.deepEqual(Array.from(bed.y), geometry.floor.y);
  assert.deepEqual(Array.from(bed.z), geometry.floor.z);
  assert.deepEqual(Array.from(bed.i), geometry.floor.i);
  assert.deepEqual(Array.from(bed.j), geometry.floor.j);
  assert.deepEqual(Array.from(bed.k), geometry.floor.k);
  assert.ok(!diagnostic.some((trace) => trace.meta?.waterbodyFrame === 'wall'));
  assert.deepEqual(diagnostic.filter((trace) => trace.meta?.waterbodyFrame !== 'bed'),
    baseline.filter((trace) => trace.meta?.waterbodyFrame !== 'bed' && trace.meta?.waterbodyFrame !== 'wall'));
});

test('bed-depth-colors changes only the forced dynamic bed style when both diagnostic modes are explicit', () => {
  const render = loadLakeTraces();
  const geometry = {
    maxDepth: 12, ve: 166.5,
    floor: { x: [0, 1, 0], y: [0, 0, 1], z: [0, -3, -12], i: [0], j: [1], k: [2], intensity: [0, 3, 12] },
    surface: { x: [], y: [], z: [], i: [], j: [], k: [] },
    walls: { px: [], py: [], pz: [], i: [], j: [], k: [] },
    shoreline: { x: [], y: [], z: [] },
  };
  const renderModes = (query) => {
    const modes = loadWaterbodyDiagnosticMode(query);
    return render(geometry, false, {}, null, {
      staticBathymetry: false,
      forceBedTrace: modes.includes('force-bed'),
      showBedSurface: modes.includes('force-bed'),
      bedDepthColors: modes.includes('force-bed') && modes.includes('bed-depth-colors'),
    });
  };
  const baseline = renderModes('');
  const colorModeAlone = renderModes('?viz3d-diagnostic=bed-depth-colors');
  const neutralBed = renderModes('?viz3d-diagnostic=force-bed').find((trace) => trace.meta?.waterbodyFrame === 'bed');
  const coloredTraces = renderModes('?viz3d-diagnostic=force-bed,bed-depth-colors');
  const coloredBed = coloredTraces.find((trace) => trace.meta?.waterbodyFrame === 'bed');
  assert.ok(!baseline.some((trace) => trace.meta?.waterbodyFrame === 'bed'), 'default high-VE suppression is unchanged');
  assert.ok(!colorModeAlone.some((trace) => trace.meta?.waterbodyFrame === 'bed'), 'color mode alone does not force the bed');
  assert.equal(neutralBed.color, undefined, 'force-bed neutral encoding uses a colorscale, not direct color');
  assert.deepEqual(JSON.parse(JSON.stringify(neutralBed.colorscale)), [[0, '#c5cdd1'], [1, '#c5cdd1']]);
  assert.deepEqual(Array.from(neutralBed.intensity), geometry.floor.intensity);
  assert.equal(neutralBed.intensitymode, 'vertex');
  const withoutStyle = (trace) => Object.fromEntries(Object.entries(trace)
    .filter(([key]) => !['color', 'intensity', 'colorscale'].includes(key)));
  assert.ok(coloredBed, 'paired modes render the same diagnostic bed');
  assert.equal(coloredBed.color, undefined);
  assert.deepEqual(Array.from(coloredBed.intensity), geometry.floor.intensity);
  assert.equal(coloredBed.intensitymode, 'vertex');
  assert.deepEqual(JSON.parse(JSON.stringify(coloredBed.colorscale)), [[0, '#75e3d7'], [1, '#173fbd']]);
  assert.equal(coloredBed.cmin, 0);
  assert.equal(coloredBed.cmax, geometry.maxDepth);
  assert.equal(coloredBed.cauto, false);
  assert.deepEqual(withoutStyle(coloredBed), withoutStyle(neutralBed), 'only bed color/intensity style changes');
  assert.deepEqual(coloredTraces.filter((trace) => trace.meta?.waterbodyFrame !== 'bed'),
    renderModes('?viz3d-diagnostic=force-bed').filter((trace) => trace.meta?.waterbodyFrame !== 'bed'));
});

test('neutral bed style diagnostic uses a constant colorscale and preserves bed data', () => {
  const render = loadLakeTraces();
  const geometry = {
    maxDepth: 12, ve: 166.5,
    floor: { x: [0, 1, 0], y: [0, 0, 1], z: [0, -3, -12], i: [0], j: [1], k: [2], intensity: [0, 3, 12] },
    surface: { x: [], y: [], z: [], i: [], j: [], k: [] },
    walls: { px: [], py: [], pz: [], i: [], j: [], k: [] },
    shoreline: { x: [], y: [], z: [] },
  };
  const renderStyle = (modes) => render(geometry, true, {}, null, {
    staticBathymetry: true,
    showBedSurface: true,
    forceBedNeutral: modes.includes('force-bed-neutral'),
    forceBedNeutralScale: modes.includes('force-bed-neutral-scale'),
  }).find((trace) => trace.meta?.waterbodyFrame === 'bed');
  const directNeutral = renderStyle(['force-bed-neutral']);
  const scaleNeutral = renderStyle(['force-bed-neutral-scale']);
  assert.ok(directNeutral && scaleNeutral, 'both neutral diagnostics render the bed');
  assert.equal(directNeutral.color, undefined, 'neutral beds must avoid direct mesh3d color encoding');
  assert.deepEqual(JSON.parse(JSON.stringify(directNeutral.colorscale)), [[0, '#c5cdd1'], [1, '#c5cdd1']]);
  assert.equal(directNeutral.intensitymode, 'vertex');
  assert.deepEqual(Array.from(directNeutral.intensity), geometry.floor.intensity);
  for (const key of ['x', 'y', 'z', 'i', 'j', 'k']) {
    assert.deepEqual(Array.from(directNeutral[key]), geometry.floor[key]);
  }
  assert.deepEqual(directNeutral.customdata, geometry.floor.intensity);
  assert.equal(directNeutral.hovertemplate, scaleNeutral.hovertemplate);
  const withoutEncoding = (trace) => Object.fromEntries(Object.entries(trace)
    .filter(([key]) => !['color', 'colorscale', 'intensity', 'intensitymode'].includes(key)));
  assert.deepEqual(withoutEncoding(directNeutral), withoutEncoding(scaleNeutral),
    'only the neutral color encoding may differ');
});

test('skip-field removes only dynamic variable traces while retaining bed and geometry', () => {
  const traces = [
    { name: 'lake bed', meta: { waterbodyFrame: 'bed' } },
    { name: 'variable', meta: { waterbodyFrame: 'field' } },
    { name: 'missing variable', meta: { waterbodyFrame: 'missing' } },
    { name: 'depth contour', meta: { waterbodyFrame: 'contour' } },
    { name: 'shoreline', meta: { shoreline: true } },
    { name: 'wet grid', meta: { networkMode: 'orthogonal' } },
  ];
  const diagnostic = filterWaterbodyDiagnosticTraces(traces, ['skip-field'], true);
  assert.deepEqual(diagnostic.map((trace) => trace.name), ['lake bed', 'depth contour', 'shoreline', 'wet grid']);
  assert.equal(filterWaterbodyDiagnosticTraces(traces, ['skip-field'], false), traces,
    'static bathymetry keeps its normal traces');
  assert.equal(filterWaterbodyDiagnosticTraces(traces, [], true), traces,
    'default rendering keeps every trace');
});

test('wall diagnostic omits only the dynamic side-wall trace', () => {
  const render = loadLakeTraces();
  const geometry = {
    maxDepth: 12, ve: 1,
    floor: { x: [0, 1, 0], y: [0, 0, 1], z: [0, -3, -12], i: [0], j: [1], k: [2], intensity: [0, 3, 12] },
    surface: { x: [], y: [], z: [], i: [], j: [], k: [] },
    walls: { px: [0, 0, 1, 1], py: [0, 0, 0, 0], pz: [0, -3, 0, -3], i: [0, 0], j: [1, 3], k: [3, 2] },
    shoreline: { x: [], y: [], z: [] },
  };
  const baseline = render(geometry, true, {}, null, { staticBathymetry: false, showBedSurface: true });
  const diagnostic = render(geometry, true, {}, null, { staticBathymetry: false, showBedSurface: true, skipWallTrace: true });
  assert.ok(baseline.some((trace) => trace.meta?.waterbodyFrame === 'wall'));
  assert.ok(!diagnostic.some((trace) => trace.meta?.waterbodyFrame === 'wall'));
  assert.deepEqual(diagnostic.filter((trace) => trace.meta?.waterbodyFrame !== 'wall'),
    baseline.filter((trace) => trace.meta?.waterbodyFrame !== 'wall'));
});

test('bed diagnostic omits only the lake-floor trace', () => {
  const render = loadLakeTraces();
  const geometry = {
    maxDepth: 12, ve: 1,
    floor: { x: [0, 1, 0], y: [0, 0, 1], z: [0, -3, -12], i: [0], j: [1], k: [2], intensity: [0, 3, 12] },
    surface: { x: [], y: [], z: [], i: [], j: [], k: [] },
    walls: { px: [0, 0, 1, 1], py: [0, 0, 0, 0], pz: [0, -3, 0, -3], i: [0, 0], j: [1, 3], k: [3, 2] },
    shoreline: { x: [], y: [], z: [] },
  };
  const baseline = render(geometry, true, {}, null, { staticBathymetry: false, showBedSurface: true });
  const diagnostic = render(geometry, true, {}, null, { staticBathymetry: false, showBedSurface: true, skipBedTrace: true });
  assert.ok(baseline.some((trace) => trace.meta?.waterbodyFrame === 'bed'));
  assert.ok(!diagnostic.some((trace) => trace.meta?.waterbodyFrame === 'bed'));
  assert.deepEqual(diagnostic.filter((trace) => trace.meta?.waterbodyFrame !== 'bed'),
    baseline.filter((trace) => trace.meta?.waterbodyFrame !== 'bed'));
});

test('bathymetry is a continuous vertex-shaded basin with a separate line-only network', () => {
  const traces = loadLakeTraces()({
    maxDepth: 12, ve: 1,
    floor: { x: [0, 1, 0], y: [0, 0, 1], z: [0, -3, -12], i: [0], j: [1], k: [2], intensity: [0, 3, 12] },
    surface: { x: [], y: [], z: [], i: [], j: [], k: [] },
    walls: { px: [], py: [], pz: [], i: [], j: [], k: [] },
    shoreline: { x: [], y: [], z: [] },
  }, true, {}, null, { staticBathymetry: true, showBedSurface: true, meshMode: 'triangles' });

  const basin = traces.find((trace) => trace.name === '湖盆水深');
  assert.equal(basin.intensitymode, 'vertex', 'depth color must interpolate continuously across the basin surface');
  assert.deepEqual(Array.from(basin.intensity), [0, 3, 12], 'use corner depths rather than one flat color per face');
  assert.equal(basin.flatshading, false, 'do not shade each triangle as a separate filled facet');
  const network = traces.find((trace) => trace.meta?.meshMode === 'triangles');
  assert.equal(network.type, 'scatter3d');
  assert.equal(network.mode, 'lines');
  assert.equal(network.i, undefined, 'network overlay must not introduce filled triangular faces');
});

test('depth projection helper interpolates wet corners without changing the default static waterbody contract', () => {
  const render = loadLakeTraces();
  const geometry = {
    maxDepth: 8, ve: 3,
    floor: { x: [0, 1, 0, 1, 2, 1], y: [0, 0, 1, 0, 0, 1], z: [0, -4, -4, 0, -8, -8],
      i: [0, 0], j: [1, 4], k: [2, 5], intensity: [0, 4, 4, 0, 8, 8], cell: [[0, 0], [0, 0], [0, 0], [1, 0], [1, 0], [1, 0]] },
    surface: { x: [0, 1, 0, 1, 2, 1], y: [0, 0, 1, 0, 0, 1], z: [0, 0, 0, 0, 0, 0],
      i: [0, 0], j: [1, 4], k: [2, 5], cell: [[0, 0], [0, 0], [0, 0], [1, 0], [1, 0], [1, 0]] },
    walls: { px: [], py: [], pz: [], i: [], j: [], k: [] },
    shoreline: { x: [], y: [], z: [] },
  };
  const original = JSON.parse(JSON.stringify(geometry));
  const traces = render(geometry, true, { bottom: [[4, 8]] }, { min: 0, max: 8 }, { staticBathymetry: true });
  const projectionContext = {};
  vm.runInNewContext(functionSource('lakeSurfaceDepthProjection'), projectionContext);
  const projected = projectionContext.lakeSurfaceDepthProjection(geometry.surface, { bottom: [[4, 8]] });
  assert.deepEqual(Array.from(projected.intensity), [4, 6, 6, 6, 6, 8], 'shared wet corners blend adjacent native cell depths');
  assert.deepEqual(Array.from(projected.customdata), [4, 4, 4, 8, 8, 8], 'hover data preserves the same native depths');
  assert.ok(traces.some((trace) => trace.meta?.waterbodyFrame === 'surface'),
    'the static preview retains its separate water surface');
  assert.ok(!traces.some((trace) => trace.meta?.waterbodyFrame === 'depthProjection'), 'no flat projection covers the water surface');
  assert.ok(!traces.some((trace) => trace.meta?.waterbodyFrame === 'bed'), 'the real bed mesh remains hidden by default');
  assert.deepEqual(geometry, original, 'the overlay cannot change the bathymetry or native mesh geometry');

  const dynamic = render(geometry, false, { bottom: [[4, 8]] }, null, { dynamicOverlay: true });
  assert.ok(!dynamic.some((trace) => trace.meta?.waterbodyFrame === 'depthProjection'), 'dynamic variable views keep a neutral water tint');
});

test('waterbody fill is visible at basin scale while remaining translucent over scientific fields', () => {
  const context = {
    _viz3dLakeStaticTraceCache: new Map(),
    lakeStaticTraceKey: () => null,
    lakeDisplayFrame: (geometry) => ({ surface: geometry.surface, wallMesh: geometry.walls, shoreline: geometry.shoreline, boundaryClipApplied: false }),
    lakeShorelineTrace: () => ({ type: 'scatter3d', name: '岸线' }),
    lakeClipMeshToBoundary: () => null,
    lakeLandTraces: () => [],
  };
  vm.runInNewContext(functionSource('lakeStaticTraces'), context);
  const surface = { x: [0, 2, 2, 0], y: [0, 0, 1, 1], z: [0, 0, 0, 0], i: [0, 0], j: [1, 2], k: [2, 3] };
  const geometry = { surface };
  const basin = context.lakeStaticTraces(geometry, {}, {}, null, '', true).surface;
  assert.equal(basin.color, '#398eae', 'use a restrained but legible blue-cyan water material');
  assert.equal(basin.opacity, 0.78, 'the basin fill remains clearly visible without a scientific overlay');
  assert.deepEqual(Array.from(basin.x), surface.x, 'water footprint continues to use the exact wet-cell mesh');
  assert.deepEqual(Array.from(basin.i), surface.i, 'the display style does not fabricate or smooth mesh topology');
  assert.ok(basin.lighting.ambient >= 0.8 && basin.lighting.specular <= 0.1,
    'soft, matte lighting keeps the water readable without glossy cues');

  const overlay = context.lakeStaticTraces(geometry, {}, { dynamicOverlay: true }, null, '', true).surface;
  assert.equal(overlay.opacity, 0.36, 'selected scientific field colors remain visible through the water surface');
});

test('static basin preview draws the source bathymetry floor below a translucent water surface', () => {
  const render = loadLakeTraces();
  const geometry = {
    maxDepth: 8, ve: 1,
    floor: { x: [0, 1, 0], y: [0, 0, 1], z: [0, -4, -8], i: [0], j: [1], k: [2], intensity: [0, 4, 8] },
    surface: { x: [0, 1, 0], y: [0, 0, 1], z: [0, 0, 0], i: [0], j: [1], k: [2], cell: [[0, 0], [0, 0], [0, 0]] },
    walls: { px: [0, 0, 1, 1], py: [0, 0, 0, 0], pz: [0, -4, 0, -4], i: [0, 0], j: [1, 3], k: [3, 2] },
    shoreline: { x: [], y: [], z: [] },
  };
  const traces = render(geometry, true, { bottom: [[4]] }, { min: 0, max: 8 },
    { staticBathymetry: true, staticBasin: true, showBedSurface: true });
  const bed = traces.find((trace) => trace.meta?.waterbodyFrame === 'bed');
  const water = traces.find((trace) => trace.meta?.waterbodyFrame === 'surface');
  assert.ok(bed && water, 'static bathymetry is presented as a basin floor and water surface');
  assert.deepEqual(Array.from(bed.z), geometry.floor.z, 'basin geometry retains source bathymetric elevations');
  assert.deepEqual(Array.from(water.x), geometry.surface.x, 'surface footprint retains the exact wet-cell mesh');
  assert.equal(water.opacity, 0.58, 'water surface reveals the measured floor below');
  assert.ok(!traces.some((trace) => trace.meta?.waterbodyFrame === 'depthProjection'),
    'static basin view does not cover the floor with a flat top-plane raster');
  assert.equal(bed.showscale, true, 'depth legend belongs to the bathymetric floor');
});

test('triangular and orthogonal selections create visibly different line overlays only', () => {
  const render = loadLakeTraces();
  const geometry = {
    maxDepth: 12, ve: 1,
    floor: { x: [0, 1, 0], y: [0, 0, 1], z: [0, -3, -12], i: [0], j: [1], k: [2], intensity: [0, 3, 12] },
    surface: { x: [], y: [], z: [], i: [], j: [], k: [] },
    walls: { px: [], py: [], pz: [], i: [], j: [], k: [] },
    shoreline: { x: [], y: [], z: [] },
  };
  const modes = ['triangles', 'orthogonal'].map((meshMode) => render(geometry, true, {}, null, { staticBathymetry: true, showBedSurface: true, meshMode }));
  const lines = modes.map((traces) => traces.find((trace) => trace.type === 'scatter3d' && trace.meta?.meshMode));
  assert.notDeepEqual(Array.from(lines[0].x), Array.from(lines[1].x));
  assert.ok(lines.every((trace) => trace.mode === 'lines' && trace.i === undefined));
});

test('dynamic lake side walls use a muted display material at ordinary vertical scale', () => {
  const render = loadLakeTraces();
  const geometry = {
    maxDepth: 12, ve: 1,
    floor: { x: [0, 1, 0], y: [0, 0, 1], z: [0, -3, -12], i: [0], j: [1], k: [2], intensity: [0, 3, 12] },
    surface: { x: [], y: [], z: [], i: [], j: [], k: [] },
    walls: { px: [0, 0, 1, 1], py: [0, 0, 0, 0], pz: [0, -3, 0, -3], i: [0, 0], j: [1, 3], k: [3, 2] },
    shoreline: { x: [], y: [], z: [] },
  };
  const wall = render(geometry, true, {}, null, { staticBathymetry: false, showBedSurface: true }).find((trace) => trace.meta?.waterbodyFrame === 'wall');
  assert.ok(wall, 'dynamic bathymetry should include its side-wall mesh');
  assert.equal(wall.color, '#628f9b', 'wet/dry walls use a restrained blue-green display material');
  assert.equal(wall.opacity, 0.48, 'dynamic wet/dry walls remain a muted display material');
});

test('static bathymetry keeps the wet-mask side wall as display-only structure', () => {
  const geometry = {
    maxDepth: 8, ve: 300,
    floor: { x: [0, 1, 0], y: [0, 0, 1], z: [0, -4, -4], i: [0], j: [1], k: [2], intensity: [0, 4, 4], cell: [[0, 0], [0, 0], [0, 0]] },
    surface: { x: [0, 1, 0], y: [0, 0, 1], z: [0, 0, 0], i: [0], j: [1], k: [2], cell: [[0, 0], [0, 0], [0, 0]] },
    walls: { px: [0, 0, 1, 1], py: [0, 0, 0, 0], pz: [0, -4, 0, -4], i: [0, 0], j: [1, 3], k: [3, 2] },
    shoreline: { x: [0, 1, 0], y: [0, 0, 1], z: [0, 0, 0] },
  };
  const render = loadLakeTraces();
  const staticTraces = render(geometry, true, { bottom: [[4]] }, { min: 0, max: 8 }, { staticBathymetry: true });
  const wall = staticTraces.find((trace) => trace.meta?.waterbodyFrame === 'wall');
  assert.ok(wall, 'static depth projection should show the wet-mask waterbody side wall');
  assert.equal(wall.meta.displayOnly, true, 'side wall is visual structure only');
  assert.equal(wall.meta.source, 'wet-mask-boundary');
  assert.equal(wall.showscale, false, 'side wall must not participate in the depth scale');
  assert.equal(wall.intensity, undefined, 'side wall must not encode or alter scientific values');
  assert.equal(wall.opacity, 0.28, 'static bathymetry uses a translucent display-only boundary while keeping the bed hidden');
  assert.deepEqual(Array.from(wall.x), geometry.walls.px, 'side wall geometry comes from supplied wet-mask mesh');
  assert.deepEqual(Array.from(wall.z), geometry.walls.pz, 'without horizontal coordinates the source wall heights remain unchanged');
  assert.ok(staticTraces.some((trace) => trace.name === '岸线'), 'the irregular wet-mask shoreline trace remains');

  const dynamicTraces = render(geometry, true, { bottom: [[4]] }, null, { staticBathymetry: false });
  assert.equal(dynamicTraces.filter((trace) => trace.meta?.waterbodyFrame === 'wall').length, 0,
    'dynamic field view retains its existing high-VE side-wall cutoff');
});

test('display shoreline is smoothly generalized without changing its sampled wet-mask coordinates', () => {
  const context = {};
  vm.runInNewContext(functionSource('smoothLakeShoreline'), context);
  const raw = {
    x: [0, 1, null, 1, 1, null, 1, 0, null, 0, 0, null],
    y: [0, 0, null, 0, 1, null, 1, 1, null, 1, 0, null],
    z: [0, 0, null, 0, 0, null, 0, 0, null, 0, 0, null],
  };
  const original = JSON.parse(JSON.stringify(raw));
  const smoothed = context.smoothLakeShoreline(raw);
  assert.deepEqual(raw, original, 'shoreline rendering must not mutate the wet-mask boundary');
  assert.ok(smoothed.x.filter(Number.isFinite).length >= 17, 'display curve applies a second display-only refinement pass');
  assert.ok(smoothed.x.some((value) => Number.isFinite(value) && !Number.isInteger(value)),
    'display curve is not restricted to square grid corners');
  assert.equal(smoothed.x.filter((value) => value === null).length, 1, 'closed shoreline remains a single path');
  assert.ok(smoothed.z.filter(Number.isFinite).every((value) => value === 0), 'display curve stays on exact shoreline elevation');
});

test('saved uploaded shoreline uses its projected vertices without smoothing and falls back to wet mask when absent', () => {
  const context = { smoothLakeShoreline: line => ({ ...line, smoothed: true }), viz3dSampledBoundary: () => false };
  vm.runInNewContext(functionSource('lakeWetMaskShorelineTrace'), context);
  vm.runInNewContext(functionSource('lakeShorelineTrace'), context);
  const boundary = { projected_polygons: [{ outer: [[10.25, 20.5], [12.75, 20.5], [12.75, 22.25]],
    holes: [[[11, 21], [11.5, 21], [11.5, 21.5]]] }],
    source_crs: { crs_type: 'geographic' }, provenance: { source: 'uploaded-boundary-shapefile' } };
  const original = JSON.parse(JSON.stringify(boundary));
  const trace = context.lakeShorelineTrace({ surface: { x: [10.25, 12.75], y: [20.5, 22.25] }, shoreline: { x: [0, 1, null], y: [0, 0, null], z: [0, 0, null] } },
    { authoritative_boundary: boundary });
  assert.deepEqual(Array.from(trace.x), [10.25, 12.75, 12.75, 10.25, null, 11, 11.5, 11.5, 11, null]);
  assert.deepEqual(Array.from(trace.y), [20.5, 20.5, 22.25, 20.5, null, 21, 21, 21.5, 21, null]);
  assert.equal(trace.meta.source, 'uploaded-boundary-projected-vertices');
  assert.equal(trace.meta.sourceVerticesPreserved, true);
  assert.equal(trace.meta.geographicPrecision, null);
  assert.match(trace.name, /uploaded-boundary-shapefile.*显示代理.*地理\/科学真实性未验证/,
    'uploaded boundary provenance remains display-only and does not claim geographic/scientific validation');
  assert.deepEqual(boundary, original, 'display must not mutate saved source geometry');
  const fallback = context.lakeShorelineTrace({ shoreline: { x: [0, 1, null], y: [0, 0, null], z: [0, 0, null] } }, {});
  assert.equal(fallback.meta.source, 'native-wet-mask-boundary-display-generalization');
  assert.equal(fallback.meta.geographicPrecision, false);
  assert.equal(fallback.smoothed, true);
});

test('saved proxy shoreline keeps projected geometry and provenance but is labeled unvalidated', () => {
  const context = { smoothLakeShoreline: line => ({ ...line, smoothed: true }), viz3dSampledBoundary: () => false };
  vm.runInNewContext(functionSource('lakeShorelineTrace'), context);
  const provenance = { source: 'recovered-local-upload-cache', status: 'proxy-display-geometry-not-scientifically-validated' };
  const boundary = { projected_polygons: [{ outer: [[10, 20], [12, 20], [12, 22]], holes: [[[10.5, 20.5], [11, 20.5], [11, 21]]] }],
    source_crs: "case projected CRS", provenance };
  const trace = context.lakeShorelineTrace({ surface: { x: [10, 12], y: [20, 22] }, shoreline: { x: [0, 1, null], y: [0, 0, null], z: [0, 0, null] } },
    { authoritative_boundary: boundary });
  assert.match(trace.name, /recovered-local-upload-cache.*显示代理.*地理\/科学真实性未验证/,
    'legend must clearly disclose proxy/unvalidated status');
  assert.deepEqual(Array.from(trace.x), [10, 12, 12, 10, null, 10.5, 11, 11, 10.5, null],
    'proxy display preserves projected outer and hole vertices');
  assert.deepEqual(Array.from(trace.y), [20, 20, 22, 20, null, 20.5, 20.5, 21, 20.5, null]);
  assert.equal(trace.meta.sourceVerticesPreserved, true);
  assert.deepEqual(trace.meta.provenance, provenance, 'source provenance remains attached to the trace');
});

test('static depth projection feathers the jagged edge inward without adding water beyond wet cells', () => {
  const context = {};
  vm.runInNewContext(functionSource('lakeShorelineFeatherTrace'), context);
  const trace = context.lakeShorelineFeatherTrace({
    surface: { x: [0, 1, 1, 0], y: [0, 0, 1, 1], z: [0, 0, 0, 0] },
    walls: { px: [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
      py: [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0] },
  });
  assert.ok(trace, 'static wet-cell edges receive a display-only feather trace');
  assert.equal(trace.type, 'mesh3d');
  assert.equal(trace.meta.displayOnly, true);
  assert.equal(trace.meta.source, 'wet-mask-boundary-inside-wet-cells');
  assert.equal(trace.i.length, 8, 'one narrow quad strip is added for each wet-cell boundary edge');
  assert.ok(trace.x.every((value) => value >= 0 && value <= 1) && trace.y.every((value) => value >= 0 && value <= 1),
    'all feather vertices remain within the source wet-cell footprint');
  assert.ok(trace.z.every((value) => value === 0), 'feather stays on the displayed water surface plane');
  assert.ok(trace.vertexcolor.some((color) => color.endsWith(',1)')) &&
    trace.vertexcolor.some((color) => color.endsWith(',0)')),
    'RGBA vertex colors fade from the edge into the wet cell');
});

test('only the static depth preview adds the wet-cell interior feather overlay', () => {
  const feather = { type: 'mesh3d', meta: { waterbodyFrame: 'shorelineAntialias' } };
  const render = loadLakeTraces(() => feather);
  const geometry = {
    maxDepth: 8, ve: 1,
    floor: { x: [], y: [], z: [], i: [], j: [], k: [], intensity: [] },
    surface: { x: [0, 1, 0], y: [0, 0, 1], z: [0, 0, 0], i: [0], j: [1], k: [2], cell: [[0, 0], [0, 0], [0, 0]] },
    walls: { px: [], py: [], pz: [], i: [], j: [], k: [] },
    shoreline: { x: [], y: [], z: [] },
  };
  const staticTraces = render(geometry, true, { bottom: [[4]] }, null, { staticBathymetry: true });
  const dynamicTraces = render(geometry, true, { bottom: [[4]] }, null, { staticBathymetry: false });
  assert.ok(staticTraces.includes(feather), 'static preview includes the edge feather');
  assert.ok(!dynamicTraces.includes(feather), 'dynamic scientific fields keep their original colors and mesh only');
});

test('static bathymetry omits the square dry-cell land mesh and retains a shoreline caveat', () => {
  const landOptions = [];
  const context = {
    _viz3dLakeStaticTraceCache: new Map(),
    viz3dSampledBoundary: () => false,
    lakeDisplayFrame: (geometry) => ({ surface: geometry.surface, wallMesh: geometry.walls, shoreline: geometry.shoreline, boundaryClipApplied: false }),
    smoothLakeShoreline: (line) => line,
    lakeShorelineTrace: geometry => ({ type: 'scatter3d', x: geometry.shoreline.x, y: geometry.shoreline.y, z: geometry.shoreline.z }),
    lakeLandTraces: (_data, opts) => { landOptions.push(opts); return opts.showLand === false ? [] : [{ name: 'dry cell tile' }]; },
  };
  vm.runInNewContext(functionSource('lakeStaticTraceKey'), context);
  vm.runInNewContext(functionSource('lakeShorelineTrace'), context);
  vm.runInNewContext(functionSource('lakeStaticTraces'), context);
  const geometry = { surface: { x: [], y: [], z: [] }, shoreline: { x: [], y: [], z: [] } };
  context.lakeStaticTraces(geometry, {}, { staticBathymetry: true }, null, '', true);
  context.lakeStaticTraces(geometry, {}, { staticBathymetry: false }, null, '', true);
  assert.equal(landOptions[0].showLand, false, 'static depth preview suppresses tiled dry-cell land');
  assert.notEqual(landOptions[1].showLand, false, 'dynamic view retains its optional land context');
  assert.match(source, /陆地高程未提供；静态预览隐藏陆地示意格；.*?；边缘淡化仅在湿单元内/s,
    'static preview must explain that no geographic land elevation or authoritative shoreline is supplied');
});

test('page template cache-busts the updated 3D shoreline renderer', () => {
  assert.match(template, /<script src="\/static\/js\/viz3d\.js\?v=174"><\/script>/,
    'the browser must request the changed shoreline renderer instead of a cached version');
  assert.match(template, /<option value="continuous" selected>结构网格连续曲面<\/option>/,
    'the default 3D view should show the selected water field without a triangular wire overlay');
  assert.match(template, /<option value="hexa">结构网格六面体（求解网格原样）<\/option>/);
  assert.doesNotMatch(template, /value="triangles"/,
    'triangle and unstructured mesh choices are not product entries');
  assert.match(template, /不提供三角网或非结构网格/);
  assert.match(template, /<option value="0" selected>自动适配湖盆<\/option>/,
    'the default scale should make the basin visible at ordinary horizontal-to-depth ratios');
  assert.match(template, /<option value="1">1× \(真实比例\)<\/option>/,
    'users can still select true vertical proportion explicitly');
  assert.match(template, /垂向放大仅改变显示比例；坐标、悬停读数与导出仍使用真实米数/,
    'vertical exaggeration remains explicitly identified as a display-only transform');
  assert.match(template, /id="viz3d-show-land" onchange="updateViz3dIso\(\)">显示岸陆示意/,
    'dry-cell land tiles should be opt-in because they are not geographic terrain');
});

test('static depth bed remains visible with neutral lighting under extreme vertical exaggeration', () => {
  const geometry = {
    maxDepth: 12, ve: 166.5,
    floor: { x: [0, 1, 0], y: [0, 0, 1], z: [0, -3, -12], i: [0], j: [1], k: [2], intensity: [0, 3, 12] },
    surface: { x: [], y: [], z: [], i: [], j: [], k: [] },
    walls: { px: [], py: [], pz: [], i: [], j: [], k: [] },
    shoreline: { x: [], y: [], z: [] },
  };
  const bed = loadLakeTraces()(geometry, true, {}, null, { staticBathymetry: true, showBedSurface: true })
    .find((trace) => trace.meta?.waterbodyFrame === 'bed');
  assert.ok(bed, 'static bathymetry preview must retain the bed trace at any VE');
  assert.equal(bed.intensitymode, 'vertex');
  assert.equal(bed.lighting.ambient, 1, 'bed color must not darken on steep faces');
  assert.equal(bed.lighting.diffuse, 0, 'neutral bed shading must not depend on triangle normals');
});

test('static and dynamic lake renders omit the bed mesh by default', () => {
  const render = loadLakeTraces();
  const geometry = {
    maxDepth: 12, ve: 1,
    floor: { x: [0, 1, 0], y: [0, 0, 1], z: [0, -3, -12], i: [0], j: [1], k: [2], intensity: [0, 3, 12] },
    surface: { x: [], y: [], z: [], i: [], j: [], k: [] },
    walls: { px: [0, 0, 1, 1], py: [0, 0, 0, 0], pz: [0, -3, 0, -3], i: [0, 0], j: [1, 3], k: [3, 2] },
    shoreline: { x: [], y: [], z: [] },
  };
  for (const opts of [{ staticBathymetry: false }, { staticBathymetry: true }]) {
    const traces = render(geometry, true, {}, null, opts);
    assert.ok(!traces.some((trace) => trace.meta?.waterbodyFrame === 'bed'),
      `${opts.staticBathymetry ? 'static' : 'dynamic'} rendering must omit the bed mesh by default`);
  }
});



test('triangular network facet lighting adds restrained spatial relief without changing field color encoding', () => {
  const context = {};
  vm.runInNewContext(`${functionSource('lakeFacetLighting')}`, context);
  const lighting = context.lakeFacetLighting();
  assert.ok(lighting.ambient >= 0.4 && lighting.ambient <= 0.6, 'ambient fill keeps shaded faces legible');
  assert.ok(lighting.diffuse >= 0.35 && lighting.diffuse <= 0.55, 'directional light reveals triangle orientation');
  assert.ok(lighting.specular > 0 && lighting.specular <= 0.12, 'a restrained highlight helps separate layers');
  assert.equal(lighting.roughness, 0.82, 'avoid glossy material cues');
  assert.deepEqual(JSON.parse(JSON.stringify(lighting)), JSON.parse(JSON.stringify(context.lakeFacetLighting())),
    'lighting is a stable display treatment');
  assert.match(source, /colorscale:style\.colorscale,cmin:style\.min,cmax:style\.max,cauto:false/,
    'quantitative variable values remain encoded only by the selected color scale');
});

test('triangular stack uses visible display-only facets and layer edges', () => {
  assert.match(source, /name:'层间侧面（显示辅助）'.*?color:'#7b8b84',opacity:\.22/s,
    'interlayer facet surfaces separate adjacent layers at normal zoom');
  assert.match(source, /line:\{color:triangles\?layerTones\[index%layerTones\.length\]:'#71858a',width:triangles\?2\.3:1\.35\}/,
    'triangular layer boundaries remain legible and retain muted display colors');
  assert.match(source, /no solver-native triangle cells/,
    'the UI continues to identify these triangles as display tessellation');
});
