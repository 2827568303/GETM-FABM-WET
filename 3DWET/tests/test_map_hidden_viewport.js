const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const source = fs.readFileSync('3DWET/app/static/js/app.js', 'utf8');
const start = source.indexOf('function initLeafletMap(g)');
const end = source.indexOf('\nfunction _cellRectangles(g)', start);
assert.ok(start >= 0 && end > start, 'Leaflet initialization is available');

const actions = [];
const maps = [];
const timers = [];
let mapOptions;
const context = vm.createContext({
    mapState: { map: null, xyMode: false },
    $: () => ({ innerHTML: '' }),
    onMapClick() {},
    _cellRectanglesXY: () => [{ s: 3299675, n: 3299725, w: 499475, e: 499525 },
        { s: 3299725, n: 3299775, w: 499525, e: 499575 }],
    L: {
        CRS: { Simple: { name: 'simple' } },
        map: (_element, options) => {
            mapOptions = options;
            const current = {
                fitBounds: bounds => { actions.push(['fitBounds', current, bounds]); return current; },
                on() {},
                invalidateSize: () => actions.push(['invalidateSize', current]),
                remove() { actions.push(['remove', current]); },
            };
            maps.push(current);
            return current;
        },
        tileLayer: () => ({ addTo() {} }),
    },
    setTimeout: callback => { timers.push(callback); },
});
vm.runInContext(source.slice(start, end), context);

// This imported case has verified lon/lat centers plus projected x/y meter
// axes. The map must use geographic bounds and fit again after a hidden tab
// receives a real size; resize alone leaves the old hidden-viewport zoom.
const bounds = { s: 29.8, w: 116.99, n: 29.84, e: 117.01 };
context.initLeafletMap({ has_lonlat: true, bounds });
assert.equal(context.mapState.xyMode, false, 'verified geographic coordinates use the geographic map');
assert.equal(JSON.stringify([actions[0][0], actions[0][2]]), JSON.stringify(['fitBounds', [[bounds.s, bounds.w], [bounds.n, bounds.e]]]));
timers[0]();
const resizeIndex = actions.findIndex(action => action[0] === 'invalidateSize' && action[1] === maps[0]);
const refitIndex = actions.findIndex((action, index) => index > resizeIndex && action[0] === 'fitBounds' && action[1] === maps[0]);
assert.ok(resizeIndex >= 0 && refitIndex > resizeIndex,
    'after a hidden page becomes visible, invalidate size then fit the grid bounds again');

// A genuinely local projected grid must remain CRS.Simple, with x/y in meters.
context.initLeafletMap({ has_lonlat: false, bounds: null, x: [499500, 499550], y: [3299700, 3299750] });
assert.equal(context.mapState.xyMode, true, 'a grid without geographic coordinates uses local XY mode');
assert.equal(mapOptions.crs, context.L.CRS.Simple);
timers[1]();
assert.ok(actions.some(action => action[0] === 'fitBounds' && action[1] === maps[1]), 'local XY grid also refits after resize');

// A delayed callback from a replaced map must not resize or refit that old case.
context.initLeafletMap({ has_lonlat: true, bounds });
const previousMap = maps[2];
context.initLeafletMap({ has_lonlat: true, bounds });
const activeMap = maps[3];
const oldActionCount = actions.length;
timers[2]();
assert.equal(context.mapState.map, activeMap, 'new case remains the active map');
assert.equal(actions.length, oldActionCount, 'stale timer must not touch an old map instance');
timers[3]();
assert.ok(actions.some(action => action[0] === 'invalidateSize' && action[1] === activeMap));
assert.ok(!actions.some(action => action[0] === 'invalidateSize' && action[1] === previousMap && action === actions[oldActionCount]));
console.log('map viewport: geographic bounds survive hidden-page resize; XY stays local PASS');
