const assert = require('node:assert/strict'), fs = require('node:fs'), vm = require('node:vm');
const source = fs.readFileSync('3DWET/app/static/js/app.js', 'utf8');
const section = (a,b) => source.slice(source.indexOf(a),source.indexOf(b,source.indexOf(a)));
const makeSelect = values => ({dataset:{},options:values.map(value=>({value,selected:true})),
    get selectedOptions(){return this.options.filter(o=>o.selected);},
    replaceChildren(){this.options=[];},appendChild(o){this.options.push(o);}});
const elements = {'calib-add-vars':makeSelect(['temp']), 'new-point-vars':makeSelect(['NO3']),
    'cal-point-select':{value:'p1'},'cal-var-select':{value:'temp'},'cal-run-compare':{},
    'cal-stats':{},'ac-convergence-chart':{getContext:()=>({})}};
const events=[], charts=[];
const state={activeCase:'test',variables3d:[{name:'temp',zh_name:'水温',en_name:'Water temperature'},{name:'NO3'}],variables2d:[],charts:{}};
let statuses=['running','completed'];
const context=vm.createContext({state,$:id=>elements[id],window:{StudioI18n:{scientificText:(zh,en)=>`${zh} / ${en}`}},
    document:{createElement:()=>({dataset:{}})},Set,Map,Number,Promise,
    setTimeout:fn=>fn(),toast:(msg)=>events.push(msg),
    loadVariables:async()=>events.push('variables'),
    updateCalComparison:async(pid,v)=>events.push(['compare',pid,v]),
    localizedChart:(ctx,config)=>{charts.push(config);return {destroy(){}};},
    api:async(url)=>{events.push(url);return url.endsWith('/start')?{success:true}:{status:statuses.shift()};}});
vm.runInContext(section('// ── Calibration workflow helpers', 'async function confirmAddCalibPoint()'),context);
(async()=>{
    // The template supplies a default temp option even before case variables load.
    // Entering calibration must still load the active case's actual variables.
    elements['cal-var-select'].options=[{value:'temp'}];
    state.variables3d=[];state.variables2d=[];events.length=0;
    context.loadVariables=async()=>{
        events.push('variables');
        state.variables3d=[{name:'diatoms_sDW',units:'gDW/m3'}];
        elements['cal-var-select'].options=[{value:'diatoms_sDW'}];
        context.populateCalibrationVariables();
    };
    context.loadCalPoints=async()=>events.push('points');
    const initSource=section('async function initCalibrate()', 'async function loadCalPoints()');
    vm.runInContext(initSource,context);
    await context.initCalibrate();
    assert.deepEqual(events,['variables','points'],'calibration must load actual result variables before points and weights');
    assert.deepEqual(elements['new-point-vars'].options.map(o=>o.value),['diatoms_sDW'],
        'the add-point dialog must offer the actual ecological variable on first entry');
    events.length=0;
    state.variables3d=[{name:'diatoms_sDW',units:'gDW/m3'}];
    await context.initCalibrate();
    assert.deepEqual(events,['points'],'already-loaded case variables must not trigger another result scan');
    state.variables3d=[{name:'temp',zh_name:'水温',en_name:'Water temperature'},{name:'NO3'}];
    elements['cal-var-select'].options=[{value:'temp'}];
    elements['new-point-vars'].options=[{value:'NO3',selected:true}];
    events.length=0;
    assert.equal(typeof context.populateCalibrationVariables,'function','calibration selectors must use real model variables');
    context.populateCalibrationVariables();
    assert.deepEqual(elements['calib-add-vars'].options.map(o=>o.value),['temp','NO3']);
    assert.deepEqual(Array.from(context.selectedCalibrationVariables('new-point-vars')),['NO3']);
    assert.match(elements['calib-add-vars'].options[0].textContent,/水温.*Water temperature/);
    await context.runCalModelAndCompare();
    assert.deepEqual(events.filter(Array.isArray),[['compare','p1','temp']]);
    assert.ok(events.indexOf('variables')>events.lastIndexOf('/api/run/status'));
    assert.equal(elements['cal-run-compare'].disabled,false);
    events.length=0;statuses=['failed'];await context.runCalModelAndCompare();
    assert.equal(events.filter(Array.isArray).length,0,'failed model must never compare stale results');
    context.renderAutoCalConvergence([{iteration:1,objective:5},{iteration:2,objective:0},{iteration:3,objective:null},{iteration:4,objective:2}]);
    assert.deepEqual(Array.from(charts[0].data.datasets[0].data),[5,0,2]);
    assert.deepEqual(Array.from(charts[0].data.datasets[1].data),[5,0,0]);
    const rows=[{dataset:{pointId:'p1',variable:'temp'},querySelector:s=>({value:s.includes('weight')?'2':'10'})}];
    elements['ac-objective-weights']={querySelectorAll:()=>rows};
    assert.deepEqual(JSON.parse(JSON.stringify(context.collectCalibrationWeights(['p1']))),[{point_id:'p1',variable:'temp',weight:2,scale:10}]);
    assert.deepEqual(Array.from(context.collectCalibrationWeights(['p2'])),[]);
    rows[0].querySelector=s=>({value:s.includes('weight')?'2':'0'});
    assert.throws(()=>context.collectCalibrationWeights(['p1']),/scale|尺度/i);
    rows[0].querySelector=s=>({value:s.includes('weight')?'2':'10'});
    Object.assign(elements,{'ac-method':{value:'pyabc'},'ac-iterations':{value:'3'},'ac-objective':{value:'rmse'},
        'ac-population-size':{value:'8'},'ac-max-simulations':{value:'120'},'ac-minimum-epsilon':{value:'0.1'},
        'ac-points':{selectedOptions:[{value:'p1'}]},'ac-progress':{}});
    let payload;
    context.document.querySelectorAll=()=>[{dataset:{module:'POM',param:'kDMinW'},closest:()=>({querySelector:s=>({value:s.includes('min')?'1':'2'})})}];
    context.api=async(url,opts)=>{payload=opts.body;return {job_id:'j'};};
    context.setInterval=()=>1;context.pollAutoCalStatus=()=>{};state.calibPointsLoaded=true;
    vm.runInContext(section('async function startAutoCal()', 'async function pollAutoCalStatus()'),context);
    await context.startAutoCal();
    assert.equal(payload.population_size,8);
    assert.equal(payload.max_simulations,120);
    assert.equal(payload.minimum_epsilon,0.1);
    assert.equal(payload.objective_weights[0].scale,10);
    const html=fs.readFileSync('3DWET/app/templates/index.html','utf8');
    for(const id of ['new-point-vars','calib-add-vars']) assert.match(html,new RegExp('<select[^>]*id="'+id+'"[^>]*multiple'));
    assert.match(html,/onclick="runCalModelAndCompare\(\)"/);
    console.log('calibration workflow: actual variables, run completion, failure isolation, zero convergence, weights PASS');
})().catch(e=>{console.error(e);process.exitCode=1;});
