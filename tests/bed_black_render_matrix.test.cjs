const assert = require('node:assert/strict');
const test = require('node:test');
const { buildScenarioMatrix, assertSingleFactorChanges, nearBlackMetrics } = require('../scripts/bed_black_render_matrix.js');

test('matrix varies camera, VE, and individual trace visibility one factor at a time', () => {
  const scenarios = buildScenarioMatrix();
  assert.equal(scenarios.length, 10);
  assert.deepEqual(scenarios.map(s => s.id), [
    'baseline', 'camera-0', 'camera-70', 'camera-minus-89',
    've-20', 've-100', 've-200',
    'hide-bed', 'hide-wall', 'hide-shoreline',
  ]);
  assert.doesNotThrow(() => assertSingleFactorChanges(scenarios));
  assert.deepEqual(scenarios.find(s => s.id === 'hide-wall').visibility,
    { bed: true, wall: false, shoreline: true });
});

test('single-factor validator rejects a bundled change', () => {
  const scenarios = buildScenarioMatrix();
  scenarios[1].ve = 200;
  assert.throws(() => assertSingleFactorChanges(scenarios), /only one factor/i);
});

test('single-factor validator rejects hiding more than one trace', () => {
  const scenarios = buildScenarioMatrix();
  scenarios.find(s => s.id === 'hide-wall').visibility.shoreline = false;
  assert.throws(() => assertSingleFactorChanges(scenarios), /only one trace visibility/i);
});

test('near-black metric reports exact screen and region counts at RGB threshold', () => {
  const rgba = new Uint8ClampedArray([
    0, 0, 0, 255, 39, 39, 39, 255,
    40, 40, 40, 255, 200, 200, 200, 255,
  ]);
  const result = nearBlackMetrics(rgba, 2, 2, { threshold: 40, region: { left: 0, top: 0, right: 1, bottom: 1 } });
  assert.equal(result.threshold, 40);
  assert.equal(result.nearBlackPixels, 2);
  assert.equal(result.totalPixels, 4);
  assert.equal(result.ratio, 0.5);
  assert.equal(result.regionNearBlackPixels, 2);
  assert.equal(result.regionPixels, 4);
  assert.equal(result.regionRatio, 0.5);
});

test('near-black metric rejects incomplete image buffers', () => {
  assert.throws(() => nearBlackMetrics(new Uint8Array(3), 1, 1), /RGBA/);
});
