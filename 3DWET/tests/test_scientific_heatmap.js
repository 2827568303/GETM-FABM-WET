// Run with node; geometry uses real backing-store pixels. A recording Canvas
// context checks the renderer's output; this is not browser visual validation.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const context = vm.createContext({ console, window: {} });
for (const file of ['scientific_style.js', 'scientific_heatmap.js']) {
    const source = path.join(__dirname, '../app/static/js', file);
    if (fs.existsSync(source)) vm.runInContext(fs.readFileSync(source, 'utf8'), context);
}
const heatmap = context.window.ScientificHeatmap;
assert.ok(heatmap, 'shared scientific heatmap API must be available');
const plain = value => JSON.parse(JSON.stringify(value));
let geometry = heatmap.layout(800, 600, 2, 3, { xc: [10, 20, 30], yc: [100, 120] });
assert.equal(geometry.mode, 'projected');
const a = geometry.center(0, 0), b = geometry.center(1, 0), c = geometry.center(0, 1);
assert.ok(c.y < a.y, 'increasing physical yc points upward');
assert.ok(Math.abs((a.y - c.y) / (b.x - a.x) - 2) < 1e-12, '10m by 20m cells keep physical aspect');
for (let j = 0; j < 2; j++) for (let i = 0; i < 3; i++) {
    const center = geometry.center(i, j);
    assert.deepEqual(plain(geometry.cellAt(center.x, center.y)), { i, j }, 'screen projection returns original indices');
}
assert.equal(geometry.cellAt(0, 0), null, 'axis margins never select a cell');
assert.equal(geometry.cellAt(geometry.plot.x - 0.01, a.y), null);
assert.equal(geometry.cellAt(geometry.plot.x + geometry.plot.width + 0.01, a.y), null);
assert.equal(geometry.cellAt(NaN, 1), null);
assert.equal(geometry.center(-1, 0), null);
assert.equal(geometry.center(0, 2), null);
const descending = heatmap.layout(800, 600, 2, 3, { xc: [30, 20, 10], yc: [120, 100] });
assert.ok(descending.center(0, 0).x > descending.center(1, 0).x, 'decreasing xc retains coordinate direction');
assert.ok(descending.center(0, 0).y < descending.center(0, 1).y);
for (let j = 0; j < 2; j++) for (let i = 0; i < 3; i++) {
    const p = descending.center(i, j);
    assert.deepEqual(plain(descending.cellAt(p.x, p.y)), { i, j });
}
const irregular = heatmap.layout(800, 600, 2, 3, { xc: [0, 10, 40], yc: [0, 20] });
assert.ok(Math.abs((irregular.center(2, 0).x - irregular.center(1, 0).x) / (irregular.center(1, 0).x - irregular.center(0, 0).x) - 3) < 1e-12, 'centers keep actual irregular spacing');
const resized = heatmap.layout(1600, 1200, 2, 3, { xc: [10, 20, 30], yc: [100, 120] });
const resizedPoint = resized.center(2, 1);
assert.deepEqual(plain(resized.cellAt(resizedPoint.x, resizedPoint.y)), { i: 2, j: 1 }, 'backing-store resize recomputes reversible geometry');
for (const coords of [{}, { xc: [0, 1], yc: [0, 1] }, { xc: [0, 0, 1], yc: [0, 1] }, { xc: [0, NaN, 1], yc: [0, 1] }, { xc: [[0, 1, 2]], yc: [0, 1] }]) {
    const fallback = heatmap.layout(800, 600, 2, 3, coords);
    assert.equal(fallback.mode, 'index');
    assert.ok(fallback.center(0, 0).y < fallback.center(0, 1).y, 'fallback retains existing row-down indexing');
    const p = fallback.center(2, 1);
    assert.deepEqual(plain(fallback.cellAt(p.x, p.y)), { i: 2, j: 1 });
}
assert.equal(heatmap.layout(300, 200, 1, 1, { xc: [1], yc: [2] }).mode, 'index', 'a single point has no physical spacing');
const nearPrecision = heatmap.layout(800, 600, 2, 3, { xc: [1, 1 + Number.EPSILON, 1 + 2 * Number.EPSILON], yc: [0, 1] });
for (let i = 0; i < 3; i++) {
    const p = nearPrecision.center(i, 0);
    assert.deepEqual(plain(nearPrecision.cellAt(p.x, p.y)), { i, j: 0 }, 'coordinate precision must not create invisible or unselectable cells');
}
const tinySpacing = heatmap.layout(800, 600, 2, 2, { xc: [0, 1e-310], yc: [0, 1e-310] });
assert.equal(tinySpacing.mode, 'index', 'physical scaling overflow must fall back to reversible index geometry');
assert.ok(Object.values(tinySpacing.plot).every(Number.isFinite), 'fallback plot geometry remains finite');
for (let j = 0; j < 2; j++) for (let i = 0; i < 2; i++) {
    const p = tinySpacing.center(i, j), rect = tinySpacing.cellRect(i, j);
    assert.ok(Object.values(p).every(Number.isFinite));
    assert.ok(Object.values(rect).every(Number.isFinite));
    assert.deepEqual(plain(tinySpacing.cellAt(p.x, p.y)), { i, j }, 'fallback keeps every cell selectable');
}
assert.equal(heatmap.layout(0, 0, 0, 0, {}).cellAt(0, 0), null);

function recordingCanvas(width = 800, height = 600) {
    const calls = [];
    let pathLines = 0;
    let transform = [1, 0, 0, 1, 0, 0];
    const ctx = { fillStyle: '', strokeStyle: '', lineWidth: 1, calls,
        save() {}, restore() {}, setTransform(...args) { transform = args; calls.push({ type: 'transform', args }); },
        clearRect(...args) { calls.push({ type: 'clear', args }); },
        fillRect(...args) { calls.push({ type: 'fill', args, color: this.fillStyle, transform: [...transform] }); },
        beginPath() { pathLines = 0; calls.push({ type: 'begin' }); }, moveTo(x, y) { calls.push({ type: 'move', x, y }); },
        lineTo(x, y) { pathLines++; calls.push({ type: 'line', x, y }); }, stroke() { calls.push({ type: 'stroke', color: this.strokeStyle, lines: pathLines }); },
        quadraticCurveTo(...args) { pathLines++; calls.push({ type:'quadratic',args }); },
        fillText(text, x, y) { calls.push({ type: 'text', text, x, y, font: this.font, transform: [...transform] }); },
        translate() {}, rotate() {}, rect() {}, closePath() { calls.push({ type: 'close' }); },
        clip(rule) { calls.push({ type: 'clip', rule }); }
    };
    return { width, height, style: { width: '400px', height: '300px' }, getContext: () => ctx, ctx };
}
const canvas = recordingCanvas();
const data = [[0, -1, null], [2, 5, 9], [1, 4, 3]];
const wetMask = [[1, 1, 1], [1, 0, 1], [1, 1, 1]];
geometry = heatmap.draw(canvas, data, { min: -1, max: 9, palette: 'viridis', wetMask, xc: [0, 10, 20], yc: [0, 20, 40] });
assert.equal(canvas.width, 800, 'draw does not resize the backing store using CSS or DPR');
assert.equal(canvas.height, 600);
assert.deepEqual(canvas.ctx.calls.find(v => v.type === 'clear').args, [0, 0, 800, 600]);
assert.deepEqual(canvas.ctx.calls.find(v => v.type === 'transform').args, [1, 0, 0, 1, 0, 0], 'incoming DPR transform cannot distort backing-store geometry');
const fillAt = (i, j) => {
    const p = geometry.center(i, j);
    return canvas.ctx.calls.find(v => v.type === 'fill' && p.x >= v.args[0] && p.x < v.args[0] + v.args[2] && p.y >= v.args[1] && p.y < v.args[1] + v.args[3] && v.args[2] < canvas.width);
};
assert.notEqual(fillAt(0, 0).color, fillAt(1, 0).color, 'zero and negative values get distinct quantitative colors');
assert.notEqual(fillAt(2, 0).color, fillAt(1, 1).color, 'wet missing data and land are different');
assert.equal(canvas.ctx.calls.filter(v => v.type === 'close').length, 4, 'wet-mask proxy keeps exterior and island loops for clipping and outlining');
assert.equal(canvas.ctx.lineJoin, 'round', 'display proxy outline uses antialiased rounded joins');
assert.equal(canvas.ctx.calls.filter(v => v.type === 'fill').length, 10, 'contour smoothing does not alter the per-cell wet/land paint');
assert.ok(canvas.ctx.calls.some(v=>v.type==='quadratic'), 'mask-derived outline corners are rounded in display pixels');
assert.ok(canvas.ctx.calls.some(v => v.type === 'text' && v.text === 'x (m)'));
assert.ok(canvas.ctx.calls.some(v => v.type === 'text' && v.text === 'y (m)'));
const wetBoolean = [[true,true,true],[true,false,true],[true,true,true]];
const dryBoolean = [[false,false,false],[false,true,false],[false,false,false]];
const displayBoundary = { coordinate_space:'bathymetry_projected_grid_coordinates',
    provenance:{source:'uploaded-boundary-shapefile'}, projected_polygons:[{outer:[[-5,-10],[25,-10],[25,50],[-5,50]],
        holes:[[[5,10],[15,10],[15,30],[5,30]]]}] };
const validationArgs={wetMask:wetBoolean,dryMask:dryBoolean,xc:[0,10,20],yc:[0,20,40],coordinateMode:'projected',rows:3,cols:3};
assert.equal(heatmap.validateBoundary(displayBoundary,validationArgs).source,'uploaded-boundary-shapefile',
    'saved outline is accepted only when all wet centers are inside and dry centers outside');
const clipped=recordingCanvas();
const clippedGeometry=heatmap.draw(clipped,data,{min:-1,max:9,wetMask:wetBoolean,dryMask:dryBoolean,
    xc:[0,10,20],yc:[0,20,40],coordinateMode:'projected',boundary:displayBoundary});
assert.equal(clippedGeometry.displayBoundary,'uploaded-boundary-shapefile','accepted boundary is reported as display-only metadata');
assert.ok(clipped.ctx.calls.some(call=>call.type==='clip'&&call.rule==='evenodd'),'the validated polygon and its holes clip displayed cells');
const invalidBoundary=JSON.parse(JSON.stringify(displayBoundary));
invalidBoundary.projected_polygons[0].outer=[[-50,-50],[-40,-50],[-40,-40],[-50,-40]];
assert.equal(heatmap.validateBoundary(invalidBoundary,validationArgs),null,'misaligned saved outlines fail the wet/dry center check');
const proxyFallback=recordingCanvas();
const proxyGeometry=heatmap.draw(proxyFallback,data,{min:-1,max:9,wetMask:wetBoolean,dryMask:dryBoolean,
    xc:[0,10,20],yc:[0,20,40],coordinateMode:'projected',boundary:invalidBoundary});
assert.equal(proxyGeometry.displayBoundary,null,'invalid saved outlines fall back to the exact wet-cell edge proxy');
assert.equal(proxyFallback.ctx.calls.filter(call=>call.type==='clip').length,1,'fallback clips only to the explicitly proxy wet-mask contour');
assert.equal(proxyGeometry.displayBoundary,null,'mask-derived contour never claims a saved geographic boundary');
const diagonalProxy=recordingCanvas();
heatmap.draw(diagonalProxy,[[1,0],[0,1]],{min:0,max:1,wetMask:[[true,false],[false,true]]});
assert.equal(diagonalProxy.ctx.calls.filter(call=>call.type==='close').length,4,
    'diagonal wet cells retain two independent proxy contour loops rather than a joined invented shore');
// A mobile canvas has the same CSS space at DPR 1, 2, or a fractional ratio.
// Glyphs and plot margins must retain that CSS size while hit testing and
// selection overlays continue to exchange backing-store pixel coordinates.
const cssWidth = 360, cssHeight = 240;
const close = (actual, expected, message) => assert.ok(Math.abs(actual - expected) < 1e-9, `${message}: ${actual} != ${expected}`);
for (const coords of [{ xc: [0, 10, 20], yc: [0, 20, 40] }, {}]) for (const pixelRatio of [1, 2, 1.25]) {
    const dprCanvas = recordingCanvas(cssWidth * pixelRatio, cssHeight * pixelRatio);
    dprCanvas.style = { width: `${cssWidth}px`, height: `${cssHeight}px` };
    const projected = heatmap.draw(dprCanvas, data, { min: -1, max: 9, wetMask, ...coords, pixelRatio });
    const logical = heatmap.layout(cssWidth, cssHeight, 3, 3, coords);
    assert.equal(projected.mode, logical.mode);
    assert.equal(projected.xMin, logical.xMin, 'physical coordinates never scale with DPR');
    assert.equal(projected.yMax, logical.yMax);
    assert.equal(dprCanvas.width, cssWidth * pixelRatio, 'drawing never resizes the backing store');
    assert.equal(dprCanvas.height, cssHeight * pixelRatio);
    assert.deepEqual(dprCanvas.ctx.calls.find(v => v.type === 'transform').args, [pixelRatio, 0, 0, pixelRatio, 0, 0], 'drawing applies the requested pixel ratio');
    assert.deepEqual(dprCanvas.ctx.calls.find(v => v.type === 'clear').args, [0, 0, cssWidth, cssHeight], 'clear uses logical dimensions with the same transform');
    for (const key of ['x', 'y', 'width', 'height']) close(projected.plot[key] / pixelRatio, logical.plot[key], `CSS-equivalent plot ${key}`);
    close(projected.projectX(logical.xMax) / pixelRatio, logical.projectX(logical.xMax), 'projectX returns backing pixels');
    close(projected.projectY(logical.yMin) / pixelRatio, logical.projectY(logical.yMin), 'projectY returns backing pixels');
    for (let j = 0; j < 3; j++) for (let i = 0; i < 3; i++) {
        const point = projected.center(i, j), logicalPoint = logical.center(i, j);
        close(point.x / pixelRatio, logicalPoint.x, 'center x uses backing pixels');
        close(point.y / pixelRatio, logicalPoint.y, 'center y uses backing pixels');
        assert.deepEqual(plain(projected.cellAt(point.x, point.y)), { i, j }, `DPR ${pixelRatio} cell hit remains reversible`);
        const rect = projected.cellRect(i, j), logicalRect = logical.cellRect(i, j);
        for (const key of ['x', 'y', 'width', 'height']) close(rect[key] / pixelRatio, logicalRect[key], `cell rectangle ${key} uses backing pixels`);
        const painted = dprCanvas.ctx.calls.filter(v => v.type === 'fill')[1 + j * 3 + i];
        close(painted.args[0] * painted.transform[0], rect.x, 'painted cell x matches backing hit geometry');
        close(painted.args[1] * painted.transform[3], rect.y, 'painted cell y matches backing hit geometry');
    }
    assert.equal(projected.cellAt(0, 0), null, 'DPR margins never select a cell');
    assert.equal(projected.cellAt(projected.plot.x + projected.plot.width + 0.01, projected.plot.y), null);
    assert.equal(projected.cellAt(NaN, 1), null);
    assert.equal(projected.cellAt('1', 1), null, 'backing pixel hit tests keep numeric input validation');
    assert.equal(projected.center(-1, 0), null);
    assert.equal(projected.cellRect(3, 0), null);
    const text = dprCanvas.ctx.calls.filter(v => v.type === 'text');
    assert.ok(text.length > 0);
    text.forEach(call => {
        close(parseFloat(call.font) * call.transform[3] / pixelRatio, 11, 'axis text remains 11 CSS pixels');
    });
}
const noMask = recordingCanvas();
heatmap.draw(noMask, [[0, null], [-1, 1]], { min: -1, max: 1 });
assert.equal(noMask.ctx.calls.find(v => v.type === 'stroke').lines, 0, 'a missing field never creates a fake coastline when mask is absent');
assert.ok(noMask.ctx.calls.some(v => v.type === 'text' && v.text === 'I / J index'));
assert.ok(!noMask.ctx.calls.some(v => v.type === 'text' && /\(m\)| m$/.test(v.text)), 'index fallback never invents metre axes or scale');
assert.throws(() => heatmap.draw(recordingCanvas(), [[1, 2], [3, 4]], { wetMask: [[1]], min: 1, max: 4 }), /mask/i);
const constant = recordingCanvas();
heatmap.draw(constant, [[0, 0]], { min: 0, max: 0 });
assert.ok(constant.ctx.calls.filter(v => v.type === 'fill').every(v => !v.color.includes('NaN')));
const empty = recordingCanvas();
heatmap.draw(empty, [[null]], { min: null, max: null });
assert.ok(empty.ctx.calls.some(v => v.type === 'text' && v.text === 'No valid data'));
const grid = recordingCanvas();
heatmap.draw(grid, data, { min: -1, max: 9, wetMask, showGrid: true });
assert.ok(grid.ctx.calls.filter(v => v.type === 'line').length > noMask.ctx.calls.filter(v => v.type === 'line').length);
const repeated = recordingCanvas();
let colorCalls = 0;
const originalColor = context.window.ScientificStyle.color;
context.window.ScientificStyle.color = (...args) => { colorCalls++; return originalColor(...args); };
heatmap.draw(repeated, [[0, 1]], { min: 0, max: 1, palette: 'cividis' });
assert.equal(colorCalls, 256, 'one lookup table is built for the palette, regardless of cell count');
heatmap.draw(repeated, [[0, 1], [-1, null]], { min: -1, max: 1, palette: 'cividis' });
assert.equal(colorCalls, 256, 'later frames reuse the palette lookup table');
console.log('scientific heatmap: reversible physical/index geometry, non-square/irregular cells, orientation, wet mask, missing/island, backing store and no invented geography PASS');
const shared=context.window.ScientificStyle;
shared.set('custom','v',{palette:'custom',stops:[[0,'#000000'],[.25,'#ff0000'],[1,'#ffffff']],nanColor:'#123456'});
let mapping=shared.resolve({caseKey:'custom',variable:'v',min:0,max:1});
const customCanvas=recordingCanvas();
heatmap.draw(customCanvas,[[.125,.625,null,0]],{min:0,max:1,style:mapping,wetMask:[[1,1,1,0]]});
assert.deepEqual(customCanvas.ctx.calls.filter(c=>c.type==='fill').slice(1).map(c=>c.color),
 ['rgb(128,0,0)','rgb(255,128,128)','#123456','#edf1f2'],'data, missing water and land use their respective actual mappings');
shared.set('custom','v',{mapping:'discrete',classes:3,stops:[[0,'#000000'],[1,'#ffffff']]});
mapping=shared.resolve({caseKey:'custom',variable:'v',min:0,max:1});
const discreteCanvas=recordingCanvas();
heatmap.draw(discreteCanvas,[[1/3-1e-10,1/3]],{min:0,max:1,style:mapping});
assert.deepEqual(discreteCanvas.ctx.calls.filter(c=>c.type==='fill').slice(1).map(c=>c.color),['rgb(43,43,43)','rgb(128,128,128)']);
