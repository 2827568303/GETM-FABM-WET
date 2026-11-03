const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const { test } = require('node:test');

const sourcePath = '3DWET/app/static/js/viz3d_mesh_mode_preference.js';

function loadPreference(initial = null, defaultMode = 'continuous') {
  const values = new Map();
  if (typeof initial === 'string') values.set('3dwet.viz3d.mesh-mode.v1', initial);
  else for (const [version, value] of Object.entries(initial || {})) values.set(`3dwet.viz3d.mesh-mode.${version}`, value);
  const select = {
    value: defaultMode,
    listeners: {},
    addEventListener(name, callback) { this.listeners[name] = callback; },
  };
  const context = vm.createContext({
    localStorage: {
      getItem(key) { return values.get(key) ?? null; },
      setItem(key, value) { values.set(key, value); },
    },
    document: { getElementById: id => id === 'viz3d-mesh-mode' ? select : null },
  });
  vm.runInContext(fs.readFileSync(sourcePath, 'utf8'), context);
  return { preference: context.Viz3dMeshModePreference, values, select };
}

test('a leftover triangle selection is not restored and falls back to continuous', () => {
  const { preference, select } = loadPreference(null, 'triangles');
  preference.bind(select);
  assert.equal(select.value, 'continuous');
});

test('legacy v1 preference is ignored and a supported template default is kept', () => {
  const { preference, select } = loadPreference('continuous', 'hexa');
  preference.bind(select);
  assert.equal(select.value, 'hexa');
});

test('mesh display preference restores a supported mode and survives later case changes', () => {
  const { preference, values, select } = loadPreference({ v2: 'curvilinear' });
  preference.bind(select);
  assert.equal(select.value, 'curvilinear');

  select.value = 'orthogonal';
  select.listeners.change();
  const nextCaseSelect = { ...select, listeners: {} };
  preference.bind(nextCaseSelect);
  assert.equal(nextCaseSelect.value, 'orthogonal');
  assert.equal(values.get('3dwet.viz3d.mesh-mode.v2'), 'orthogonal');
});

test('invalid, stored-triangle, or inaccessible mesh preference falls back to continuous', () => {
  const invalid = loadPreference({ v2: 'native-triangles' });
  invalid.preference.bind(invalid.select);
  assert.equal(invalid.select.value, 'continuous');

  const storedTriangle = loadPreference({ v2: 'triangles' });
  storedTriangle.preference.bind(storedTriangle.select);
  assert.equal(storedTriangle.select.value, 'continuous');

  const context = vm.createContext({
    localStorage: { getItem() { throw new Error('blocked'); }, setItem() { throw new Error('blocked'); } },
  });
  vm.runInContext(fs.readFileSync(sourcePath, 'utf8'), context);
  const select = { value: 'triangles', addEventListener() {} };
  assert.doesNotThrow(() => context.Viz3dMeshModePreference.bind(select));
  assert.equal(select.value, 'continuous');
});
