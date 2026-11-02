/* Shared, side-effect-free helpers for the frame-19 bed-render diagnostic. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.BedBlackRenderMatrix = api;
})(typeof globalThis === 'object' ? globalThis : this, function () {
  'use strict';

  const baseline = Object.freeze({
    cameraElevation: 34,
    ve: 50,
    visibility: Object.freeze({ bed: true, wall: true, shoreline: true }),
  });

  function scenario(id, label, factor, changes = {}) {
    return {
      id, label, factor,
      cameraElevation: changes.cameraElevation ?? baseline.cameraElevation,
      ve: changes.ve ?? baseline.ve,
      visibility: { ...(changes.visibility || baseline.visibility) },
    };
  }

  function buildScenarioMatrix() {
    return [
      scenario('baseline', 'Baseline · 34° / VE 50× / all three visible', null),
      scenario('camera-0', 'Camera only · 0°', 'camera', { cameraElevation: 0 }),
      scenario('camera-70', 'Camera only · 70°', 'camera', { cameraElevation: 70 }),
      scenario('camera-minus-89', 'Camera only · −89°', 'camera', { cameraElevation: -89 }),
      scenario('ve-20', 'VE only · 20×', 've', { ve: 20 }),
      scenario('ve-100', 'VE only · 100×', 've', { ve: 100 }),
      scenario('ve-200', 'VE only · 200×', 've', { ve: 200 }),
      scenario('hide-bed', 'Visibility only · bed hidden', 'visibility', { visibility: { bed: false, wall: true, shoreline: true } }),
      scenario('hide-wall', 'Visibility only · wall hidden', 'visibility', { visibility: { bed: true, wall: false, shoreline: true } }),
      scenario('hide-shoreline', 'Visibility only · shoreline hidden', 'visibility', { visibility: { bed: true, wall: true, shoreline: false } }),
    ];
  }

  function equal(a, b) {
    return JSON.stringify(a) === JSON.stringify(b);
  }

  function assertSingleFactorChanges(scenarios) {
    if (!Array.isArray(scenarios) || !scenarios.length || scenarios[0].id !== 'baseline') {
      throw new Error('Scenario matrix must start with baseline');
    }
    const ids = new Set();
    const base = scenarios[0];
    for (const entry of scenarios) {
      if (ids.has(entry.id)) throw new Error(`Duplicate scenario id: ${entry.id}`);
      ids.add(entry.id);
      if (entry === base) continue;
      const changed = [];
      if (entry.cameraElevation !== base.cameraElevation) changed.push('camera');
      if (entry.ve !== base.ve) changed.push('ve');
      const changedVisibilityKeys = Object.keys(base.visibility)
        .filter(key => entry.visibility[key] !== base.visibility[key]);
      if (!equal(entry.visibility, base.visibility)) changed.push('visibility');
      const expected = entry.factor;
      if (!expected || changed.length !== 1 || changed[0] !== expected) {
        throw new Error(`${entry.id} must change only one factor; changed: ${changed.join(', ') || 'none'}`);
      }
      if (expected === 'visibility' && changedVisibilityKeys.length !== 1) {
        throw new Error(`${entry.id} must change only one trace visibility; changed: ${changedVisibilityKeys.join(', ') || 'none'}`);
      }
    }
    return true;
  }

  function nearBlackMetrics(rgba, width, height, options = {}) {
    const threshold = options.threshold ?? 40;
    if (!Number.isInteger(width) || width < 1 || !Number.isInteger(height) || height < 1 ||
        !rgba || rgba.length !== width * height * 4) {
      throw new Error('Expected a complete RGBA image buffer with matching dimensions');
    }
    if (!Number.isInteger(threshold) || threshold < 0 || threshold > 256) {
      throw new Error('Threshold must be an integer from 0 through 256');
    }
    const region = options.region || { left: 0.12, top: 0.10, right: 0.88, bottom: 0.84 };
    for (const key of ['left', 'top', 'right', 'bottom']) {
      if (!Number.isFinite(region[key]) || region[key] < 0 || region[key] > 1) {
        throw new Error(`Region ${key} must be a fraction from 0 through 1`);
      }
    }
    if (region.right <= region.left || region.bottom <= region.top) throw new Error('Region must have positive area');
    const x0 = Math.floor(width * region.left), x1 = Math.ceil(width * region.right);
    const y0 = Math.floor(height * region.top), y1 = Math.ceil(height * region.bottom);
    let nearBlackPixels = 0, regionNearBlackPixels = 0, regionPixels = 0;
    for (let y = 0; y < height; y++) for (let x = 0; x < width; x++) {
      const offset = (y * width + x) * 4;
      const isOpaque = rgba[offset + 3] > 0;
      const isNearBlack = isOpaque && Math.max(rgba[offset], rgba[offset + 1], rgba[offset + 2]) < threshold;
      if (isNearBlack) nearBlackPixels++;
      if (x >= x0 && x < x1 && y >= y0 && y < y1) {
        regionPixels++;
        if (isNearBlack) regionNearBlackPixels++;
      }
    }
    const totalPixels = width * height;
    return {
      threshold, region, totalPixels, nearBlackPixels,
      ratio: nearBlackPixels / totalPixels,
      regionPixels, regionNearBlackPixels,
      regionRatio: regionNearBlackPixels / regionPixels,
    };
  }

  return { buildScenarioMatrix, assertSingleFactorChanges, nearBlackMetrics };
});
