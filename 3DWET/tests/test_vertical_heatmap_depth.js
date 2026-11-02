// Regression tests for dynamic, per-time physical vertical geometry.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(require('node:path').join(__dirname, '../app/static/js/app.js'), 'utf8');
const start = source.indexOf('function _vheatDepthFrac(');
const helperStart = source.indexOf('function _vheatBuildPhysicalCells(');
const context = vm.createContext({ Number, Array, Math, isFinite });
context.window = {};
const renderStart = source.indexOf('function drawVerticalHeatmap(');
assert.ok(start >= 0 && helperStart > start && renderStart > helperStart, 'app.js must expose sigma and physical-cell geometry helpers');
vm.runInContext(source.slice(start, renderStart), context);
const build = context._vheatBuildPhysicalCells;

const fixture = {
    series: [[10, 10, null], [5, 6, null], [1, 2, null]],
    times: ['t0', 't1', 't2'],
    // Nonuniform and time-varying physical centers, positive downward.
    layer_center_depth_m: [[8, 13, 9], [3, 7, null], [0.5, 1.5, 2]],
    layer_center_depth_source: 'GETM hn+zc cell-center geometry',
};
const result = build(fixture);
assert.equal(result.error, null);
assert.equal(result.cells.length, 6, 'null values omit only their display cell');
const cell = (time, level) => result.cells.find(v => v.timeIndex === time && v.levelIndex === level);
assert.deepEqual(JSON.parse(JSON.stringify([cell(0, 0).top, cell(0, 0).bottom])), [5.5, 10.5]);
assert.deepEqual(JSON.parse(JSON.stringify([cell(1, 0).top, cell(1, 0).bottom])), [10, 16]);
assert.notEqual(cell(0, 0).top, cell(1, 0).top, 'vertical geometry must change with time');
assert.equal(cell(2, 1), undefined, 'null value or null geometry must not be painted as zero');
assert.equal(result.depthMax, 16);
assert.ok(result.cells.every(v => v.center > 0 && v.top >= 0 && v.bottom > v.top));
const missingValue = build({ ...fixture, series: [[10, 10, null], [null, 6, null], [1, 2, null]] });
assert.deepEqual(JSON.parse(JSON.stringify([missingValue.cells.find(v => v.timeIndex === 0 && v.levelIndex === 0).top,
    missingValue.cells.find(v => v.timeIndex === 0 && v.levelIndex === 0).bottom])), [5.5, 10.5],
    'a null value does not collapse adjacent layers because geometry includes all layer centers');

for (const bad of [
    { ...fixture, layer_center_depth_m: undefined },
    { ...fixture, layer_center_depth_m: [[1], [2], [3]] },
    { ...fixture, layer_center_depth_source: '' },
    { ...fixture, layer_center_depth_m: [[1, 2, 3], [2, 2, 4], [3, 4, 5]] },
    { ...fixture, layer_center_depth_m: [[1, 2, 3], [null, 4, 5], [3, 5, 6]] },
]) {
    assert.ok(build(bad).error, 'missing, malformed, ambiguous or nonmonotonic geometry must be reported');
}

const legacy = build({ series: fixture.series, times: fixture.times, layers: [-1, -0.5, 0] });
assert.ok(legacy.error, 'legacy sigma cannot masquerade as physical depth');

let rendered;
const plot = { innerHTML: '' };
context.$ = () => plot;
context.ModelDates = { plotlyAxis: times => ({ x: times.map((_, i) => i * 10), labels: times, axis: { type: 'linear' } }) };
context.Plotly = { react: (...args) => { rendered = args; } };
context.window.Plotly = context.Plotly;
const renderEnd = source.indexOf('\n// ── Calibration', renderStart);
vm.runInContext(source.slice(renderStart, renderEnd), context);
context.drawVerticalHeatmap('plot', fixture, 'depth');
assert.ok(rendered, 'depth view must render with Plotly');
const physicalTraces = rendered[1].filter(trace => trace.fill === 'toself');
assert.equal(physicalTraces.length, 6);
const movingCell = physicalTraces.find(trace => trace.customdata[0][2] === 't0' && trace.name === '层 0');
const movedCell = physicalTraces.find(trace => trace.customdata[0][2] === 't1' && trace.name === '层 0');
assert.deepEqual(JSON.parse(JSON.stringify(movingCell.y)), [5.5, 5.5, 10.5, 10.5, 5.5]);
assert.deepEqual(JSON.parse(JSON.stringify(movedCell.y)), [10, 10, 16, 16, 10]);
assert.match(movingCell.hovertemplate, /实际深度中心/);
assert.equal(rendered[2].yaxis.range[1], 0, 'surface stays at top for positive-down depths');
context.drawVerticalHeatmap('plot', { ...fixture, layer_center_depth_m: undefined }, 'depth');
assert.match(plot.innerHTML, /真实深度几何缺失/);
context.drawVerticalHeatmap('plot', { ...fixture, layer_center_depth_m: undefined, layers: [-1, -.5, 0] }, 'sigma');
assert.ok(rendered[1].some(trace => trace.type === 'heatmap'), 'legacy sigma mode remains a heatmap');
context.drawVerticalHeatmap('plot', { ...fixture, layer_center_depth_m: undefined, layers: [-1, -.5, 0] }, 'level');
assert.ok(rendered[1].some(trace => trace.type === 'heatmap'), 'legacy layer mode remains a heatmap');
console.log('vertical heatmap dynamic depth geometry, nonuniform layers, changing hn/zc, nulls and strict source contract PASS');
