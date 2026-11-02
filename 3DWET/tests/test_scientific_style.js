// Run with node; exercise the actual shared range/color module without a DOM.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const context = vm.createContext({ console, window: {} });
const source = path.join(__dirname, '../app/static/js/scientific_style.js');
if (fs.existsSync(source)) vm.runInContext(fs.readFileSync(source, 'utf8'), context);
const style = context.window.ScientificStyle;
assert.ok(style, 'shared scientific style API must be available');
assert.equal(typeof style.legendTicks,'function','narrow legends need a readable tick budget without rounding away field differences');
const narrowLegend=style.legendTicks(15.1497488,15.1497555,195,10);
assert.ok(narrowLegend.labels.length<=3);
assert.equal(narrowLegend.values[0],15.1497488);assert.equal(narrowLegend.values.at(-1),15.1497555);
assert.equal(new Set(narrowLegend.labels).size,narrowLegend.labels.length);
assert.equal(style.legendTicks(0,100,1000,10).labels.length,5,'wide export/desktop legends retain detail');
const plain = value => JSON.parse(JSON.stringify(value));
const colorDefaults={stops:[[0,'#75e3d7'],[1,'#173fbd']],reverse:false,mapping:'continuous',classes:5,nanColor:'#c9cbd0'};

assert.deepEqual(plain(style.get('lake-a', 'temp')), { ...colorDefaults,palette: 'lake', mode: 'auto', min: null, max: null });
assert.equal(style.color(0, 'lake'), 'rgb(117,227,215)', 'default lake colors start with saturated cyan');
const snapshot = style.get('lake-a', 'temp');
snapshot.palette = 'viridis';
assert.equal(style.get('lake-a', 'temp').palette, 'lake', 'get cannot mutate stored state');
let resolved = style.resolve({ caseKey: 'lake-a', variable: 'temp', min: -3, max: 0 });
assert.equal(resolved.min, -3);
assert.equal(resolved.max, 0, 'zero and negative values are valid');
style.set('lake-a', 'temp', { mode: 'locked' });
resolved = style.resolve({ caseKey: 'lake-a', variable: 'temp', min: 15.149, max: 15.150 });
assert.equal(resolved.min, 15.149);
assert.equal(style.resolve({ caseKey: 'lake-a', variable: 'temp', min: 10, max: 20 }).max, 15.150, 'locked range survives later frames');
assert.equal(style.resolve({ caseKey: 'lake-b', variable: 'temp', min: 10, max: 20 }).max, 20, 'cases do not share limits');
assert.equal(style.resolve({ caseKey: 'lake-a', variable: 'salt', min: 10, max: 20 }).max, 20, 'variables do not share limits');
style.set('lake-a', 'temp', { palette: 'cividis' });
assert.equal(style.resolve({ caseKey: 'lake-a', variable: 'temp', min: 1, max: 2 }).min, 15.149, 'palette changes retain a lock');
style.set('lake-a', 'temp', { mode: 'custom', min: -1, max: 1 });
const custom = plain(style.get('lake-a', 'temp'));
for (const patch of [{ min: 2 }, { min: 1, max: 1 }, { max: Infinity }, { min: null }, { palette: 'rainbow' }, { mode: 'other' }]) {
    assert.throws(() => style.set('lake-a', 'temp', patch), /range|palette|mode/i);
    assert.deepEqual(plain(style.get('lake-a', 'temp')), custom, 'invalid settings do not partially modify stored state');
}
resolved = style.resolve({ caseKey: 'lake-a', variable: 'temp', min: -100, max: 100 });
assert.equal(resolved.min, -1);
assert.equal(resolved.max, 1);
style.set('lake-a', 'temp', { mode: 'auto' });
assert.equal(style.resolve({ caseKey: 'lake-a', variable: 'temp', min: 30, max: 40 }).min, 30, 'returning to auto releases the lock');

for (const [min, max] of [[15.149, 15.150], [-0.000003, 0.000002], [1e12, 1e12 + 1], [1e-20, 1.01e-20], [-1e308, 1e308]]) {
    const ticks = style.ticks(min, max);
    assert.ok(ticks.values.length >= 2);
    assert.equal(ticks.values[0], min);
    assert.equal(ticks.values.at(-1), max);
    assert.equal(new Set(ticks.labels).size, ticks.values.length, `ticks must be distinct for ${min}..${max}`);
    assert.ok(ticks.values.every(Number.isFinite));
}
for (const [min, max] of [[0.001, 1], [-1, -0.001]]) {
    const ticks = style.ticks(min, max);
    assert.equal(new Set(ticks.labels).size, ticks.values.length, 'retaining nonzero endpoints must also retain distinct labels');
    ticks.values.forEach((value, index) => {
        assert.ok(value === 0 || Number(ticks.labels[index]) !== 0, `nonzero tick ${value} cannot be labelled zero`);
    });
}
assert.deepEqual(plain(style.ticks(0, 0)), { values: [0], labels: ['0'] }, 'all-zero field has one truthful tick');
assert.deepEqual(plain(style.ticks(-4, -4)), { values: [-4], labels: ['-4'] });
assert.deepEqual(plain(style.ticks(null, null)), { values: [], labels: [] });
assert.deepEqual(plain(style.ticks(3, 1)), { values: [], labels: [] });
style.set('empty', 'temp', { mode: 'locked' });
resolved = style.resolve({ caseKey: 'empty', variable: 'temp', min: null, max: null });
assert.equal(resolved.noData, true);
assert.equal(resolved.min, null, 'empty data must never turn into a zero field');
assert.equal(style.get('empty', 'temp').min, null, 'an empty frame cannot establish a lock');
assert.equal(style.resolve({ caseKey: 'empty', variable: 'temp', min: 0, max: 0 }).max, 0);
assert.equal(style.resolve({ caseKey: 'empty', variable: 'temp', min: 1, max: 9 }).max, 0, 'constant zero can establish a lock');
for (const palette of ['lake', 'cividis', 'viridis']) {
    assert.match(style.color(0.5, palette), /^rgb\(\d+,\d+,\d+\)$/);
    assert.equal(style.color(-1, palette), style.color(0, palette));
    assert.equal(style.color(2, palette), style.color(1, palette));
    style.set('palette', palette, { palette });
    const map = style.resolve({ caseKey: 'palette', variable: palette, min: 0, max: 1 });
    assert.equal(map.colorscale[0][1], style.color(0, palette));
    assert.equal(map.colorscale.at(-1)[1], style.color(1, palette));
}
assert.notEqual(style.color(0.5, 'lake'), style.color(0.5, 'viridis'));
assert.equal(style.color(0.5, 'constructor'), style.color(0.5, 'lake'), 'unknown palette names safely use lake');

// A reload creates a fresh JavaScript global with no access to the first
// module's Map. Only the browser storage adapter carries state across loads.
function loadWithStorage(storage) {
    const reloaded = vm.createContext({ console, window: { localStorage: storage } });
    vm.runInContext(fs.readFileSync(source, 'utf8'), reloaded);
    return reloaded.window.ScientificStyle;
}
const stored = new Map();
let writes = 0;
const storage = { getItem: key => stored.get(key) ?? null, setItem: (key, value) => { writes++; stored.set(key, String(value)); } };
const firstLoad = loadWithStorage(storage);
firstLoad.set('persistent-a', 'temp', { mode: 'custom', min: -2, max: 2, palette: 'viridis' });
firstLoad.set('persistent-b', 'temp', { mode: 'custom', min: 20, max: 30 });
firstLoad.set('persistent-a', 'salt', { mode: 'custom', min: 10, max: 15 });
assert.equal(stored.size, 1, 'one namespaced storage item owns the settings');
const [storageKey, serialized] = [...stored.entries()][0];
assert.match(storageKey, /scientific.*v\d/i, 'storage key is scoped and versioned');
assert.equal(JSON.parse(serialized).version, 2, 'stored payload has a schema version');
const secondLoad = loadWithStorage(storage);
assert.deepEqual(plain(secondLoad.get('persistent-a', 'temp')), { ...colorDefaults,palette: 'viridis', mode: 'custom', min: -2, max: 2 }, 'a new global restores saved settings');
assert.equal(secondLoad.get('persistent-b', 'temp').min, 20, 'reload keeps cases isolated');
assert.equal(secondLoad.get('persistent-a', 'salt').max, 15, 'reload keeps variables isolated');
const unchanged = stored.get(storageKey), writesBeforeInvalid = writes;
assert.throws(() => secondLoad.set('persistent-a', 'temp', { min: 3 }), /range/i);
assert.equal(writes, writesBeforeInvalid, 'invalid patches never write storage');
assert.equal(stored.get(storageKey), unchanged, 'invalid patches cannot overwrite the last valid persisted state');
secondLoad.set('persistent-a', 'temp', { mode: 'locked' });
secondLoad.resolve({ caseKey: 'persistent-a', variable: 'temp', min: null, max: null });
assert.equal(loadWithStorage(storage).get('persistent-a', 'temp').min, null, 'empty frame leaves persisted lock unestablished');
secondLoad.resolve({ caseKey: 'persistent-a', variable: 'temp', min: 0, max: 0 });
const thirdLoad = loadWithStorage(storage);
assert.equal(thirdLoad.resolve({ caseKey: 'persistent-a', variable: 'temp', min: -9, max: 9 }).max, 0, 'first valid lock, including constant zero, survives reload');
assert.equal(thirdLoad.get('persistent-a', 'temp').palette, 'viridis');

const corrupt = loadWithStorage({ getItem: () => '{broken json', setItem() {} });
assert.deepEqual(plain(corrupt.get('persistent-a', 'temp')), { ...colorDefaults,palette: 'lake', mode: 'auto', min: null, max: null }, 'malformed storage cannot prevent startup');
corrupt.set('new', 'var', { mode: 'custom', min: 1, max: 2 });
assert.equal(corrupt.get('new', 'var').max, 2, 'settings remain usable after corrupt storage');
const unknownVersion = loadWithStorage({ getItem: () => JSON.stringify({ ...JSON.parse(serialized), version: 999 }), setItem() {} });
assert.equal(unknownVersion.get('persistent-a', 'temp').mode, 'auto', 'unknown schema is ignored');
const invalidRecord = JSON.parse(serialized);
invalidRecord.entries.push({ caseKey: 'bad', variable: 'var', palette: 'rainbow', mode: 'custom', min: -1, max: 1 });
invalidRecord.entries.push({ caseKey: 'bad', variable: 'range', palette: 'lake', mode: 'custom', min: 3, max: 2 });
const partiallyCorrupt = loadWithStorage({ getItem: () => JSON.stringify(invalidRecord), setItem() {} });
assert.equal(partiallyCorrupt.get('persistent-a', 'temp').min, -2, 'valid records survive alongside invalid records');
assert.equal(partiallyCorrupt.get('bad', 'var').palette, 'lake');
assert.equal(partiallyCorrupt.get('bad', 'range').mode, 'auto');
const failing = loadWithStorage({ getItem() { throw new Error('read denied'); }, setItem() { throw new Error('quota exceeded'); } });
assert.doesNotThrow(() => failing.set('memory', 'temp', { mode: 'custom', min: -4, max: 0 }));
assert.equal(failing.get('memory', 'temp').min, -4, 'failed persistence retains current in-memory settings');
failing.set('memory', 'salt', { mode: 'locked' });
assert.doesNotThrow(() => failing.resolve({ caseKey: 'memory', variable: 'salt', min: -1, max: 1 }));
assert.equal(failing.resolve({ caseKey: 'memory', variable: 'salt', min: -3, max: 3 }).max, 1, 'failed persistence still locks later frames');
const deniedWindow = {};
Object.defineProperty(deniedWindow, 'localStorage', { get() { throw new Error('storage access denied'); } });
const deniedContext = vm.createContext({ console, window: deniedWindow });
assert.doesNotThrow(() => vm.runInContext(fs.readFileSync(source, 'utf8'), deniedContext), 'even accessing the storage property can be blocked');
assert.doesNotThrow(() => deniedWindow.ScientificStyle.set('blocked', 'temp', { palette: 'cividis' }));
assert.equal(deniedWindow.ScientificStyle.get('blocked', 'temp').palette, 'cividis');
const quotaStorage = { getItem: storage.getItem, setItem() { throw new Error('quota exceeded'); } };
const quotaLoad = loadWithStorage(quotaStorage);
quotaLoad.set('persistent-a', 'temp', { palette: 'cividis' });
assert.equal(quotaLoad.get('persistent-a', 'temp').palette, 'cividis', 'quota failure keeps the new in-memory value');
assert.equal(loadWithStorage(storage).get('persistent-a', 'temp').palette, 'viridis', 'quota failure leaves the last persisted value recoverable');
console.log('scientific style: per-case/variable auto/lock/custom, atomic validation, precise ticks, zero/negative/constant/empty, palettes, reload/corrupt/failing storage PASS');
