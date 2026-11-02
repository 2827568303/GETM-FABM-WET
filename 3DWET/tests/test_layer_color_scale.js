const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const {test} = require('node:test');

const styleSource = fs.readFileSync('3DWET/app/static/js/scientific_style.js', 'utf8');
const vizSource = fs.readFileSync('3DWET/app/static/js/viz3d.js', 'utf8');
const appSource = fs.readFileSync('3DWET/app/static/js/app.js', 'utf8');

function layerPayload(level) {
    const base = level === 0 ? 10 : 15.46;
    return {
        shape: [1, 1, 2],
        xc: [0, 100],
        yc: [0],
        bottom: [[4, 8]],
        sigma: [level === 0 ? -0.5 : 0],
        data: [[[base, base + 1]]],
        min: base,
        max: base + 1,
        layer_indices: [level],
        total_layers: 2,
        units: 'degC',
        long_name: 'temperature',
    };
}

test('3D water-body colour scale changes with the selected physical layer', async () => {
    const plots = [];
    const element = {innerHTML: '', dataset: {}, on() {}};
    const status = {textContent: '', dataset: {}};
    const context = vm.createContext({
        console,
        URL,
        URLSearchParams,
        Plotly: {newPlot: async (_el, traces, layout) => plots.push({traces, layout})},
        document: {getElementById: id => id === 'viz3d-status' ? status : element},
        fetch: async url => ({json: async () => layerPayload(Number(new URL(url, 'http://localhost').searchParams.get('level')))}),
        window: {},
    });
    context.window = context;
    vm.runInContext(styleSource, context);
    vm.runInContext(vizSource, context);
    await context.render3DWaterBody('temp', 0, {level: 0, ve: 1, caseKey: 'dianchi', timeLabel: '2023-01-01'});
    await context.render3DWaterBody('temp', 0, {level: 1, ve: 1, caseKey: 'dianchi', timeLabel: '2023-01-01'});
    const field = plot => plot.traces.find(trace => trace.meta && trace.meta.scientificField === true);
    const bottom = field(plots[0]);
    const surface = field(plots[1]);
    assert.equal(bottom.cmin, 10);
    assert.equal(bottom.cmax, 11);
    assert.equal(surface.cmin, 15.46);
    assert.equal(surface.cmax, 16.46);
    assert.notDeepEqual(bottom.colorbar.ticktext, surface.colorbar.ticktext);
    assert.equal(bottom.meta.layerOrdinals[0], 0);
    assert.equal(surface.meta.layerOrdinals[0], 1);
});

test('2D colour scale follows the requested layer and a flat variable ignores the layer', async () => {
    const published = [];
    const painted = [];
    const elements = new Map();
    function element(id) {
        if (!elements.has(id)) elements.set(id, {id, value: '', textContent: '', dataset: {}, style: {}, disabled: false, title: '', options: []});
        return elements.get(id);
    }
    element('viz2d-var').value = 'temp';
    element('viz2d-time').value = '0';
    element('viz2d-level').value = '0';
    element('viz2d-play-start').value = '0';
    element('viz2d-play-end').value = '0';
    const state = {activeCasePath: 'dianchi', caseRevision: 1, outputRevision: 0, viz2dRequest: 0};
    const context = vm.createContext({
        console, state, URL, URLSearchParams,
        window: {
            ScientificStyle: null,
            ScientificWorkspace: {
                syncFrom() {}, loading() {}, isPlaying() { return false; },
                dateLabel() { return '2023-01-01'; },
                publish(_kind, meta) { published.push(meta); },
            },
        },
        document: {getElementById: element, querySelector: () => null},
        $: element,
        fmt: (value, digits = 2) => Number(value).toFixed(digits),
        resultLabel: (_data, name) => name,
        drawHeatmap(_id, _data, min, max) { painted.push([min, max]); },
        drawColorbar() {},
        setViz2dBoundarySummary() {},
        api: async url => {
            const level = Number(new URL(url, 'http://localhost').searchParams.get('level'));
            const name = new URL(url, 'http://localhost').searchParams.get('var');
            if (name === 'elev') {
                return {data: [[1, 2]], min: 1, max: 2, mean: 1.5, shape: [1, 2], units: 'm',
                    level: null, level_applies: false, layer_contrast: null};
            }
            const base = level === 0 ? 10 : 15.46;
            return {
                data: [[base, base + 1]], min: base, max: base + 1, mean: base + 0.5, shape: [1, 2], units: 'degC',
                level, level_applies: true,
                layer_contrast: {
                    bottom_index: 0, surface_index: 1, bottom_mean: 11.25, surface_mean: 16.48,
                    mean_abs_diff: 5.23, max_abs_diff: 5.46, well_mixed: false,
                },
            };
        },
    });
    context.window.ScientificStyle = {
        resolve(input) { return {...input, mode: 'auto', palette: 'lake', colorscale: [[0, '#000000'], [1, '#ffffff']]}; },
    };
    vm.runInContext(appSource.slice(appSource.indexOf('async function updateViz2d('), appSource.indexOf('// Variable change handler')), context);
    await context.updateViz2d();
    element('viz2d-level').value = '1';
    await context.updateViz2d();
    assert.deepEqual(painted, [[10, 11], [15.46, 16.46]]);
    assert.equal(published[0].range.min, 10);
    assert.equal(published[1].range.min, 15.46);
    assert.match(element('viz2d-info').textContent, /最大 5.4600/);
    assert.doesNotMatch(element('viz2d-info').textContent, /垂向差异很小/);
    element('viz2d-var').value = 'elev';
    element('viz2d-level').value = '4';
    await context.updateViz2d();
    assert.match(element('viz2d-info').textContent, /没有垂向层/);
    assert.deepEqual(painted.at(-1), [1, 2]);
});
