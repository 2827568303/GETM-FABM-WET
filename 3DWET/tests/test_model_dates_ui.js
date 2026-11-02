const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const elements = new Map();
const element = id => {
    if (!elements.has(id)) elements.set(id, {value:'', style:{}, textContent:'', getContext:()=>({}), classList:{remove(){}}, appendChild(){}});
    return elements.get(id);
};
const calls = [];
let chart, heatmap;
const context = vm.createContext({console, Date,
    document:{getElementById:element, querySelector:()=>null, querySelectorAll:()=>[], addEventListener(){}, createElement:()=>({style:{},remove(){}})},
    window:{addEventListener(){}, Plotly:{}},
    Chart: function(ctx, cfg) { chart = cfg; this.destroy=()=>{}; },
    Plotly:{react(el,traces,layout){ heatmap={traces,layout}; }},
    _ppStatus(){},
    setTimeout:()=>0, clearInterval(){}, confirmStudio:async()=>true,
});
vm.runInContext(fs.readFileSync('3DWET/app/static/js/model_dates.js','utf8'), context);
vm.runInContext(fs.readFileSync('3DWET/app/static/js/app.js','utf8'), context);
context.request = async (url, opts) => { calls.push({url,opts}); return {error:'stub response'}; };
vm.runInContext('api = request; state.activeCase = "Test";',context);
(async () => {
    context.renderCellTsChart(['2024-02-29 12:00:00','2025-01-01'],[1,2],'temp','C');
    assert.deepEqual(Array.from(chart.data.labels),['2024-DOY060 12:00:00','2025-DOY001']);
    context.drawVerticalHeatmap('heat',{times:['2024-02-29','2024-03-02'], series:[[1,2]],layers:[0]},'level');
    assert.equal(heatmap.layout.xaxis.type,'linear');
    assert.deepEqual(Array.from(heatmap.layout.xaxis.ticktext),['2024-DOY060','2024-DOY062']);
    assert.equal(heatmap.traces[0].x[1] - heatmap.traces[0].x[0],172800000);
    assert.ok(heatmap.traces[0].hovertemplate.includes('customdata'), 'hover shows ordinal dates');
    assert.deepEqual(Array.from(heatmap.traces[0].customdata[0]),['2024-DOY060','2024-DOY062']);
    element('time-start').value='2024-DOY060 12:00:00';
    element('time-stop').value='2025-DOY001 00:00:00';
    element('time-dt').value='15'; element('time-step2d').value='1';
    await context.saveTimeSettings();
    assert.equal(calls.at(-1).opts.body.start,'2024-02-29 12:00:00','solver API receives ISO');
    assert.equal(calls.at(-1).opts.body.stop,'2025-01-01 00:00:00');
    const count = calls.length;
    element('time-start').value='2023-DOY366';
    await context.saveTimeSettings();
    assert.equal(calls.length,count,'invalid ordinal cannot reach solver API');
    element('time-start').value='2025-DOY002'; element('time-stop').value='2025-DOY001';
    await context.saveTimeSettings();
    assert.equal(calls.length,count,'end must be after start');
    context._prefillBuildDates('2024-02-29','2024-12-31');
    assert.equal(element('build-start').value,'2024-DOY060 00:00:00');
    assert.equal(element('build-stop').value,'2024-DOY366 00:00:00');
    element('build-start').value='2024-DOY060 00:00:00';
    element('build-stop').value='2024-DOY061 00:00:00';
    await context.buildCase();
    assert.equal(calls.at(-1).opts.body.start,'2024-02-29 00:00:00');
    assert.equal(calls.at(-1).opts.body.stop,'2024-03-01 00:00:00');
    element('cal-data-values').value='[{"time":"2024-DOY060","value":15}]';
    await context.saveCalData();
    assert.equal(calls.at(-1).opts.body.values[0].time,'2024-02-29');
    const html=fs.readFileSync('3DWET/app/templates/index.html','utf8');
    assert.ok(html.indexOf('model_dates.js') < html.indexOf('viz3d.js'));
    assert.ok(!/placeholder=["'][^"']*\d{4}-\d{2}-\d{2}/.test(html));
    assert.ok(!/type=["'](?:date|datetime-local|month)["']/.test(html));
    console.log('model dates UI: charts, heatmap hover, inputs and solver ISO compatibility PASS');
})().catch(error=>{ console.error(error); process.exitCode=1; });
