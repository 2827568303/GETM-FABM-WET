const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const source = fs.readFileSync('3DWET/app/static/js/app.js', 'utf8');
const start = source.indexOf('function drawMapLayer()');
const end = source.indexOf('\nasync function loadMapFieldVars()', start);
assert.ok(start >= 0 && end > start, 'drawMapLayer source is available');

const rectangles = [];
const layer = { addTo() {} };
const context = vm.createContext({
    L: {
        layerGroup: () => layer,
        rectangle: (bounds, options) => { rectangles.push({ bounds, options }); return { addTo() {} }; },
    },
    _cellRectangles: () => [0, 1, 2, 3].map(i => ({ j: 0, i, s: i, n: i + 1, w: 0, e: 1 })),
    _cellRectanglesXY: () => [],
    _mapColorScale: value => Number.isFinite(value) ? `value:${value}` : null,
    $: () => ({ value: 'result', innerHTML: '' }),
});
vm.runInContext(`
    let mapState = {
        grid: { depth: [[1, 1, 1, 1]] },
        map: { removeLayer() {}, fitBounds() {} },
        xyMode: false,
        field: { values: [[-2.00000004e20, null, -0.25, 1.5]], min: -2.00000004e20, max: 1.5, var: 'greens_sDW' },
    };
    ${source.slice(start, end)}
    drawMapLayer();
`, context);

assert.equal(rectangles.length, 2, 'skips the GETM fill sentinel and null while retaining valid negative and positive wet values');
assert.deepEqual(rectangles.map(r => r.options.fillColor), ['value:-0.25', 'value:1.5']);
console.log('Map fill-value rendering passed');
