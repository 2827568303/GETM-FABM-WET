const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const source = fs.readFileSync('3DWET/app/static/js/app.js', 'utf8');
const start = source.indexOf('async function updateCalComparison(');
const end = source.indexOf('\nfunction showScatterModal()', start);
assert.ok(start >= 0 && end > start, 'comparison function is available');

const captured = [];
const elements = {
    'cal-point-select': { value: 'station-1' },
    'cal-var-select': { value: 'temp' },
    'cal-chart': { getContext: () => ({}) },
    'cal-stats': { innerHTML: '' },
    'scatter-meta': { innerHTML: '' },
    'scatter-metrics': { innerHTML: '' },
};
elements['cal-point-select'].options = [{ text: 'Station 1' }];
elements['cal-point-select'].selectedIndex = 0;
const state = { charts: {} };
const payload = {
    simulated: {
        times: ['2020-01-01 00:00:00', '2020-01-01 00:01:00'],
        // Native column values are [time][layer], with depths moving over time.
        values: [[11, 12, 13], [21, 22, 23]],
        center_depth: [[0.1, 0.3, 0.5], [0.2, 0.4, 0.6]],
        unit: 'degC', geometry_source: 'hn+zc',
    },
    observed: [
        { time: '2020-01-01 00:00:30', depth_m: 0.35, value: 17.2 },
        { time: '2020-01-01 00:01:00', depth_m: 0.5, value: 22.9 },
    ],
    // Backend values have already been interpolated at each observation's
    // native time and depth. Never infer a layer from the 2D native matrix.
    scatter_pairs: [
        { time: '2020-01-01 00:00:30', sim: 16.5, obs: 17.2, depth_m: 0.35 },
        { time: '2020-01-01 00:00:30', sim: 0, obs: 0.2, depth_m: 0.5 },
        { time: '2020-01-01 00:01:00', sim: 22, obs: 22.9, depth_m: 0.5 },
        { time: '2020-01-01 00:02:00', sim: NaN, obs: 23, depth_m: 0.5 },
        { time: '2020-01-01 00:03:00', sim: 24, obs: Infinity, depth_m: 0.5 },
    ],
};
const context = vm.createContext({
    state, $: id => elements[id],
    api: async () => payload,
    localizedChart: (_ctx, value) => { captured.push(value); return { destroy() {} }; },
    ModelDates: { parse: text => ({ date: new Date(text.replace(' ', 'T') + 'Z') }), chartLabels: values => values },
    calibrationScientificText: zh => zh,
    escapeHtml: value => String(value).replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch])),
    resultLabel: () => '温度',
    computeMetrics: () => ({}), renderMetricsHTML: () => '',
});
vm.runInContext(source.slice(start, end), context);

(async () => {
    await context.updateCalComparison();
    const chart = captured[0];
    const [simulated, observed] = chart.data.datasets;
    assert.ok(simulated.data.every(Number.isFinite), 'simulated chart values must be scalars, never layer arrays');
    assert.deepEqual(Array.from(simulated.data), [16.5, 0, 22], 'retain zero and filter non-finite pairs');
    assert.deepEqual(Array.from(observed.data), [17.2, 0.2, 22.9], 'plot exact observations including same-time different-depth pairs');
    assert.deepEqual(Array.from(chart.data.labels), [
        '2020-01-01 00:00:30', '2020-01-01 00:00:30', '2020-01-01 00:01:00',
    ], 'do not deduplicate valid observations that share a timestamp');
    assert.match(simulated.label, /配对|paired/i, 'legend must explain this is the matched observation-time/depth series');
    assert.ok(observed.pointRadius >= 4, 'observation marks need a visible radius');
    assert.equal(observed.backgroundColor, '#f59e0b', 'observation marks need a solid visible fill');
    assert.equal(observed.pointBorderColor, '#9a5a00', 'observation marks need a contrasting outline');
    assert.ok(observed.borderWidth > 0, 'observation marks need a visible outline');
    assert.match(chart.options.scales.y.title.text, /degC/, 'accept current API unit field');
    payload.simulated.unit = '';
    payload.simulated.units = 'degC';
    await context.updateCalComparison();
    assert.match(captured[1].options.scales.y.title.text, /degC/, 'also accept the legacy units field');
    payload.scatter_pairs = [];
    await context.updateCalComparison();
    assert.match(elements['cal-stats'].innerHTML, /无有效配对|No valid pairs/i, 'empty pairs need an explicit empty state');
    assert.equal(captured.length, 2, 'do not draw native multi-layer data without valid scalar pairs');
    payload.scatter_pairs = [{ time: '2020-01-01 00:00:30', sim: 16.5, obs: 17.2 }];
    const scatterLayout = {};
    const scatterContext = vm.createContext({
        state: { calLastData: payload }, $: id => elements[id],
        showModal() {}, computeMetrics: () => ({}), renderMetricsHTML: () => '',
        escapeHtml: value => String(value).replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch])),
        ModelDates: { format: text => text },
        Plotly: { newPlot: (_id, _traces, layout) => Object.assign(scatterLayout, layout) },
    });
    const scatterStart = source.indexOf('function showScatterModal()');
    const scatterEnd = source.indexOf('\n// ── Auto Calibration', scatterStart);
    vm.runInContext(source.slice(scatterStart, scatterEnd), scatterContext);
    scatterContext.showScatterModal();
    assert.match(scatterLayout.xaxis.title.text, /degC/, 'scatter axis accepts unit and legacy units fields');
    assert.match(scatterLayout.yaxis.title.text, /degC/, 'scatter model axis uses the same physical unit');
    assert.match(elements['scatter-meta'].innerHTML, /degC/);
    console.log('calibration comparison: paired scalars, duplicate-time points, units, visible markers, empty state PASS');
})().catch(error => { console.error(error); process.exitCode = 1; });
