const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('3DWET/app/static/js/app.js', 'utf8');
function harness(name, next) {
    const pending = [], plots = [], errors = [];
    const elements = new Proxy({}, {get: (o, id) => o[id] ||= {
        value: id.includes('var') ? 'temp' : id === 'ts-mode' ? 'lake' : '0',
        getContext: () => ({}), style: {}, innerHTML: ''}});
    const context = vm.createContext({state: {caseRevision: 1, charts: {}, timeLabels: []},
        $: id => elements[id], document: {getElementById: id => elements[id]}, window: {},
        api: () => new Promise(resolve => pending.push(resolve)),
        localizedChart: (ctx, cfg) => {plots.push(cfg); return {destroy() {}};},
        drawHeatmap: (id, data) => plots.push(data), drawColorbar() {},
        resultLabel: (d,n) => n, ModelDates: {chartLabels: v => v, format: v => v},
        toast: message => errors.push(message)});
    vm.runInContext(source.slice(source.indexOf('async function '+name+'('), source.indexOf(next, source.indexOf('async function '+name+'('))), context);
    return {pending, plots, errors, elements, context, run: () => context[name]()};
}
const data = value => ({data: [[value]], min:value, max:value, units:'C',
    sigma:[-.5], profile:[value], times:['2020-01-01'], values:[value]});
(async () => {
    for (const [name,next] of [['updateViz3d','async function updateViz3dAvg('],
        ['updateViz3dAvg','// ── Time Series'], ['extractTimeseries','// ── Vertical Heatmap']]) {
        // The end marker may follow helper declarations; only call the real entry point.
        const h = harness(name,next);
        const older = h.run(), resolveOlder = h.pending.shift();
        const newer = h.run(); h.pending.shift()(data(22)); await newer;
        resolveOlder(data(11)); await older;
        assert.equal(h.plots.length, 1, name+': late response replaced newer plot');
        const stale = h.run(), resolveStale = h.pending.shift();
        h.context.state.caseRevision++;
        resolveStale(data(33)); await stale;
        assert.equal(h.plots.length, 1, name+': previous case response rendered');
        const failing = h.run(), resolveFailing = h.pending.shift();
        const good = h.run(); h.pending.shift()(data(44)); await good;
        const before = h.errors.length;
        resolveFailing({error:'obsolete failure'}); await failing;
        assert.equal(h.errors.length, before, name+': obsolete error shown');
    }
    console.log('Profile, depth mean and time series: latest response wins; stale cases/errors ignored PASS');
})().catch(error => {console.error(error); process.exitCode = 1;});
