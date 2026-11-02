const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {test}=require('node:test');
const workspace=fs.readFileSync('3DWET/app/static/js/scientific_workspace.js','utf8');
const appSource=fs.readFileSync('3DWET/app/static/js/app.js','utf8');
function environment(patch={}) {
    const elements=new Map(),timers=new Map(),calls=[];let timerId=0;
    function element(id) {
        if(!elements.has(id))elements.set(id,{id,value:'',max:'20',options:[],style:{},dataset:{},textContent:'',replaceChildren(){},
            setAttribute(){},addEventListener(){},classList:{toggle(){},remove(){},contains(){return false;}},
            set innerHTML(value){this.options=[];this.value='';},
            appendChild(option){this.options.push(option);if(this.options.length===1)this.value=String(option.value);}});
        return elements.get(id);
    }
    for(const kind of ['viz2d','viz3d']) {
        element(kind==='viz3d'?'viz3d-iso-var':'viz2d-var').value='temp';
        element(kind==='viz3d'?'viz3d-iso-time':'viz2d-time').value='0';
        element(kind+'-speed').value='1';
    }
    const state={activeCasePath:'A',caseRevision:1,variables2d:[],variables3d:[],...patch};
    const context=vm.createContext({window:{StudioIcons:{node:()=>({})},performance:{now:()=>Date.now()},requestAnimationFrame:callback=>{queueMicrotask(()=>callback(Date.now()));return 1;},cancelAnimationFrame(){}},state,console,$:element,
        document:{readyState:'loading',hidden:false,getElementById:element,querySelector:()=>null,addEventListener(){},querySelectorAll:()=>[],createElement:()=>({dataset:{}})},
        setTimeout:(fn,delay=0)=>{const id=++timerId;timers.set(id,{fn,delay});return id;},clearTimeout:id=>timers.delete(id),
        ModelDates:{format:x=>x||''},setInterval:fn=>{timers.set(++timerId,fn);return timerId;},clearInterval:id=>timers.delete(id),
        updateViz2d:async()=>calls.push(['2d',Number(element('viz2d-time').value)]),
        updateViz3dIso:async()=>calls.push(['3d',Number(element('viz3d-iso-time').value)]),
        localizedVariableLabel:v=>v.name,populateCalibrationVariables(){},fmt:String});
    context.verticalResultSelectIds=new Set(['viz3d-var','viz3d-avg-var']);
    context.updateResultVariableSearch=()=>{};
    const verticalStart=appSource.indexOf('function hasVerticalResultDimension('),verticalEnd=appSource.indexOf('\nfunction resultVariableOptionLabel',verticalStart);
    vm.runInContext(appSource.slice(verticalStart,verticalEnd),context);
    const labelStart=appSource.indexOf('function resultVariableOptionLabel('),labelEnd=appSource.indexOf('// ── Utilities',labelStart);
    vm.runInContext(appSource.slice(labelStart,labelEnd),context);
    const inventoryStart=appSource.indexOf('const resultInventoryRequests = new Map();'),inventoryEnd=appSource.indexOf('\nfunction clearResultInventory',inventoryStart);
    vm.runInContext(appSource.slice(inventoryStart,inventoryEnd),context);
    vm.runInContext(workspace,context);
    return {context,state,element,timers,calls,w:context.window.ScientificWorkspace};
}

test('each legacy result stream uses its own frame count and actual labels',async()=>{
    const e=environment({timeLabels:['wrong0','wrong1','wrong2','wrong3'],timeLabels2d:['surface0','surface1'],timeLabels3d:['volume0','volume1','volume2','volume3']});
    e.w.activate('viz2d');assert.equal(e.element('viz2d-time').max,'1');
    assert.equal(e.element('viz2d-time-label').textContent,'surface0');
    e.w.onNavigate('viz2d');await e.w.step('viz2d',10);
    assert.equal(e.element('viz2d-time').value,'1','2D cannot request frames that only exist in 3D');
    assert.equal(e.element('viz2d-time-label').textContent,'surface1');
    e.w.activate('viz3d');assert.equal(e.element('viz3d-iso-time').max,'3');
});

test('variable source metadata overrides the view stream and preserves legacy sources',async()=>{
    const e=environment({variables3d:[{name:'temp',time_axis:'volume',ntimesteps:3,nlev:2}],
        variables2d:[{name:'temp',time_axis:'wrong',ntimesteps:8},{name:'flux',time_axis:'legacy',ntimesteps:2}],
        resultTimeAxes:{volume:['2026-01-01 00:00:00','2026-01-01 06:00:00','2026-01-01 12:00:00'],legacy:['2005-05-01','2005-05-02']},
        timeLabels2d:['unrelated0','unrelated1','unrelated2','unrelated3'],timeLabels3d:['also wrong']});
    e.w.activate('viz2d');assert.equal(e.element('viz2d-time').max,'2','2D slice of a volume follows the volume source');
    await e.w.step('viz2d',1);assert.equal(e.element('viz2d-time-label').textContent,'2026-01-01 06:00:00');
    e.element('viz2d-var').value='flux';e.element('viz2d-time').value='10';e.w.syncFrom('viz2d');
    assert.equal(e.element('viz2d-time').max,'1');assert.equal(e.element('viz2d-time').value,'1');
    assert.equal(e.element('viz2d-time-label').textContent,'2005-05-02');
    assert.equal(e.w.variableMetadata('temp').nlev,2,'same-name variables follow 3D-first API resolution');
});

test('playback stops at the selected variable final frame',async()=>{
    const e=environment({variables2d:[{name:'temp',time_labels:['first','last'],ntimesteps:2}],timeLabels:['wrong0','wrong1','wrong2','wrong3']});
    e.w.onNavigate('viz2d');e.w.togglePlay('viz2d');
    // The first actual output must finish drawing before playback advances.
    await new Promise(resolve=>setImmediate(resolve));assert.equal(e.timers.size,1);
    const playbackEntry=[...e.timers].find(([,timer])=>timer.delay>50);assert.ok(playbackEntry);e.timers.delete(playbackEntry[0]);playbackEntry[1].fn();await new Promise(resolve=>setImmediate(resolve));assert.deepEqual(e.calls,[['2d',0],['2d',1]]);assert.equal(e.timers.size,0);
});

test('switching views retains the same variable actual date instead of another stream index',()=>{
    const e=environment({variables3d:[{name:'temp',time_axis:'volume',ntimesteps:3}],resultTimeAxes:{volume:['t0','t6','t12']},
        timeLabels2d:['other0','other1','other2','other3','other4'],timeLabels3d:['other0','other1']});
    e.element('viz2d-var').options=[{value:'temp'}];e.element('viz3d-iso-var').options=[{value:'temp'}];
    e.element('viz2d-time').value='2';e.w.syncFrom('viz2d');e.w.activate('viz3d');
    assert.equal(e.element('viz3d-iso-time').value,'2');assert.equal(e.element('viz3d-iso-time-label').textContent,'t12');
});

test('view synchronization finds the actual date when the source frame positions change',()=>{
    const e=environment({variables3d:[{name:'temp',time_axis:'volume',ntimesteps:3}],resultTimeAxes:{volume:['t0','t6','t12']}});
    e.element('viz3d-iso-var').options=[{value:'temp'}];e.element('viz2d-time').value='2';e.w.syncFrom('viz2d');
    e.state.resultTimeAxes.volume=['t0','t3','t6','t9','t12'];e.state.variables3d[0].ntimesteps=5;
    e.w.activate('viz3d');assert.equal(e.element('viz3d-iso-time').value,'4');
    assert.equal(e.element('viz3d-iso-time-label').textContent,'t12');
});

test('empty authoritative axes do not display dates from a previous stream',()=>{
    const e=environment({variables3d:[{name:'temp',time_axis:'empty',ntimesteps:0}],resultTimeAxes:{empty:[]},timeLabels:['stale'],timeLabels3d:['stale']});
    e.w.activate('viz3d');assert.equal(e.element('viz3d-iso-time').max,'0');
    assert.equal(e.element('viz3d-iso-time-label').textContent,'帧 0');assert.equal(e.element('viz3d-play').disabled,true);
});

test('inventory stores deduplicated source axes and sets each selected variable range',async()=>{
    const e=environment();
    e.context.api=async()=>({'2d':[{name:'surface',time_axis:'surface',ntimesteps:2}],
        '3d':[{name:'temp',time_axis:'volume',ntimesteps:3,nlev:2,ndim:4}],
        time_axes:{surface:['s0','s1'],volume:['v0','v1','v2']},time_labels_2d:['s0','s1'],time_labels_3d:['v0','v1','v2'],timesteps_2d:2,timesteps_3d:3});
    vm.runInContext(appSource.slice(appSource.indexOf('async function loadVariables('),appSource.indexOf('// ── Dashboard')),e.context);
    await e.context.loadVariables();
    assert.ok(e.state.resultTimeAxes,'inventory must retain the real source time axes');
    assert.deepEqual(JSON.parse(JSON.stringify(e.state.resultTimeAxes)),{surface:['s0','s1'],volume:['v0','v1','v2']});
    e.element('viz2d-var').value='surface';e.w.syncFrom('viz2d');assert.equal(e.element('viz2d-time').max,'1');
    assert.equal(e.element('viz3d-iso-time').max,'2');
});

test('2D layer choices use the variable physical layer count',async()=>{
    const e=environment({nlev:17,variables3d:[{name:'temp',ndim:4,nlev:3,ntimesteps:1}]});
    vm.runInContext(appSource.slice(appSource.indexOf('async function onViz2dVarChange('),appSource.indexOf('// ── Viz2d Interaction Tools')),e.context);
    await e.context.onViz2dVarChange();
    assert.deepEqual(e.element('viz2d-level').options.map(o=>o.value),[2,1,0]);
});

test('all main and linked 3D renders receive the selected variable actual date',async()=>{
    const e=environment({variables3d:[{name:'temp',ndim:4,nlev:3,time_axis:'native',ntimesteps:2}],
        resultTimeAxes:{native:['2026-10-15 00:00:00','2026-10-15 06:00:00']},timeLabels:['wrong0','wrong1']});
    e.element('viz3d-iso-time').value='1';e.element('viz3d-iso-ve').value='100';e.element('viz3d-opacity').value='1';
    const rendered=[];e.context.render3DCloud=async(...args)=>rendered.push(args);e.element('viz3d-iso-render').value='cloud';
    vm.runInContext(appSource.slice(appSource.indexOf('async function updateViz3dIso('),appSource.indexOf('async function updateViz3d()')),e.context);
    await e.context.updateViz3dIso();assert.equal(rendered[0].at(-1).timeLabel,'2026-10-15 06:00:00');
    assert.equal(e.element('viz3d-iso-layer').max,'2');
    e.element('viz3d-section-axis').value='xz';e.element('viz3d-section-index').value='0';
    e.context.window.renderSpatialSection=async(...args)=>{rendered.push(args);return {};};
    vm.runInContext(appSource.slice(appSource.indexOf('async function updateSpatialSection('),appSource.indexOf('// ── Calibration workflow helpers')),e.context);
    await e.context.updateSpatialSection();assert.equal(rendered[1].at(-1).timeLabel,'2026-10-15 06:00:00');
});

test('2D frame scaling uses the returned current-frame min/max without a playback-range request',async()=>{
    const e=environment({variables2d:[{name:'temp',ntimesteps:2,time_labels:['t0','t1']}]});
    const styleInputs=[];
    e.context.rangeRequests=0;
    vm.runInContext("window.ScientificWorkspace.resolvePlaybackRange=async()=>{rangeRequests++;return {min:-100,max:100};}",e.context);
    e.context.window.ScientificStyle={get:()=>({mode:'auto',palette:'lake'}),resolve:input=>{styleInputs.push(input);return {...input,mode:'auto'};}};
    e.context.api=async url=>{
        const time=Number(new URL(url,'http://localhost').searchParams.get('time'));
        return {data:[[7+time,12+time]],min:7+time,max:12+time,mean:9.5+time,shape:[1,2]};
    };
    e.context.drawHeatmap=()=>{};e.context.drawColorbar=()=>{};e.context.resultLabel=(d,n)=>n;
    vm.runInContext(appSource.slice(appSource.indexOf('async function updateViz2d('),appSource.indexOf('// Variable change handler')),e.context);
    await e.context.updateViz2d();e.element('viz2d-time').value='1';
    await e.context.updateViz2d();
    assert.equal(e.context.rangeRequests,0,'auto playback must not request full-window bounds per frame');
    assert.deepEqual(styleInputs.map(({min,max})=>[min,max]),[[7,12],[8,13]]);
    assert.equal(e.w.current('viz2d').range.min,8);assert.equal(e.w.current('viz2d').range.max,13);
});

test('3D frame rendering skips the playback-range request and passes no fixed window bounds',async()=>{
    const e=environment({variables3d:[{name:'temp',ndim:4,nlev:2,ntimesteps:2,time_labels:['t0','t1']}]});
    e.element('viz3d-iso-time').value='1';e.element('viz3d-iso-render').value='cloud';
    let rangeRequests=0;const rendered=[];
    e.context.rangeRequests=0;
    vm.runInContext("window.ScientificWorkspace.resolvePlaybackRange=async()=>{rangeRequests++;return {min:-100,max:100};}",e.context);
    e.context.render3DCloud=async(...args)=>rendered.push(args);
    vm.runInContext(appSource.slice(appSource.indexOf('async function updateViz3dIso('),appSource.indexOf('async function updateViz3d()')),e.context);
    await e.context.updateViz3dIso();
    assert.equal(e.context.rangeRequests,0,'3D playback must not request full-window bounds per frame');
    assert.equal(Object.hasOwn(rendered[0].at(-1),'playbackRange'),false);
});

test('the 2D main summary and profile time label use the same variable source date',async()=>{
    const e=environment({variables3d:[{name:'temp',ndim:4,nlev:3,time_axis:'native',ntimesteps:2}],
        resultTimeAxes:{native:['2026-10-15 00:00:00','2026-10-15 06:00:00']},timeLabels:['wrong0','wrong1']});
    e.element('viz2d-time').value='1';e.element('viz2d-level').value='2';
    e.context.api=async()=>({data:[[5]],min:5,max:5,mean:5,shape:[1,1]});
    e.context.drawHeatmap=()=>{};e.context.drawColorbar=()=>{};e.context.resultLabel=(d,n)=>n;
    vm.runInContext(appSource.slice(appSource.indexOf('async function updateViz2d('),appSource.indexOf('// Variable change handler')),e.context);
    await e.context.updateViz2d();assert.equal(e.w.current('viz2d').date,'2026-10-15 06:00:00');
    e.element('viz3d-var').value='temp';e.element('viz3d-time').value='1';e.context.api=async()=>({error:'no profile'});
    vm.runInContext(appSource.slice(appSource.indexOf('async function updateViz3d()'),appSource.indexOf('async function updateViz3dAvg(')),e.context);
    await e.context.updateViz3d();assert.match(e.element('viz3d-time-label').textContent,/2026-10-15 06:00:00/);
});

test('a scalar field cannot be silently rendered as a 3D water volume',async()=>{
    const e=environment({variables2d:[{name:'temp',ndim:3,time_axis:'scalar',ntimesteps:1}],resultTimeAxes:{scalar:['s0']}});
    e.element('viz3d-iso-render').value='cloud';const rendered=[];e.context.render3DCloud=async(...args)=>rendered.push(args);
    e.context.toast=()=>{};
    vm.runInContext(appSource.slice(appSource.indexOf('async function updateViz3dIso('),appSource.indexOf('async function updateViz3d()')),e.context);
    await e.context.updateViz3dIso();assert.equal(rendered.length,0);
    assert.equal(e.element('viz3d-iso-render').value,'surface2d','variables without vertical layers use the explicitly labeled variable-height surface mode');
    assert.match(e.element('viz3d-iso-render-hint').textContent,/没有真实垂向层|no real vertical layers/);
});

test('new inventories default to a usable volume without hiding scalar selections',async()=>{
    const e=environment();e.element('viz2d-var').value='';e.element('viz3d-iso-var').value='';
    const data={'3d':[{name:'D',ndim:2},{name:'salt',ndim:4,nlev:4},{name:'temp',ndim:4,nlev:3}],timesteps_3d:2};
    e.context.api=async()=>data;
    vm.runInContext(appSource.slice(appSource.indexOf('async function loadVariables('),appSource.indexOf('// ── Dashboard')),e.context);
    await e.context.loadVariables();
    for(const id of ['viz2d-var','viz3d-iso-var','viz3d-var','viz3d-avg-var'])assert.equal(e.element(id).value,'temp');
    assert.ok(e.element('viz3d-iso-var').options.some(v=>v.value==='D'),'height mode retains scalar fields');
    e.element('viz3d-iso-var').value='D';await e.context.loadVariables();assert.equal(e.element('viz3d-iso-var').value,'D','a deliberate selection is preserved');
    delete data['3d'][2];data['3d']=data['3d'].filter(Boolean);e.element('viz3d-iso-var').value='';
    await e.context.loadVariables();assert.equal(e.element('viz3d-iso-var').value,'salt','without temperature the first real volume is usable');
});

test('entering 2D with a loaded inventory populates the actual surface layer',async()=>{
    const e=environment({nlev:20,variables3d:[{name:'temp',ndim:4,nlev:3,ntimesteps:2}]});
    e.element('viz2d-var').options=[{value:'temp'}];const requested=[];
    e.context.updateViz2d=async()=>requested.push(e.element('viz2d-level').value);
    vm.runInContext(appSource.slice(appSource.indexOf('async function initViz2d('),appSource.indexOf('async function updateViz2d(')),e.context);
    vm.runInContext(appSource.slice(appSource.indexOf('async function onViz2dVarChange('),appSource.indexOf('// ── Viz2d Interaction Tools')),e.context);
    await e.context.initViz2d();assert.equal(e.element('viz2d-level').value,'2');
    assert.deepEqual(requested,['2']);
});

test('2D entry waits for the coalesced current inventory request',async()=>{
    const e=environment(),pending=[],requested=[];let entered=false;
    e.context.api=()=>new Promise(resolve=>pending.push(resolve));
    e.context.updateViz2d=async()=>requested.push([e.element('viz2d-var').value,e.element('viz2d-level').value]);
    vm.runInContext(appSource.slice(appSource.indexOf('async function loadVariables('),appSource.indexOf('// ── Dashboard')),e.context);
    vm.runInContext(appSource.slice(appSource.indexOf('async function initViz2d('),appSource.indexOf('async function updateViz2d(')),e.context);
    vm.runInContext(appSource.slice(appSource.indexOf('async function onViz2dVarChange('),appSource.indexOf('// ── Viz2d Interaction Tools')),e.context);
    const entering=e.context.initViz2d().then(()=>{entered=true;}),newer=e.context.loadVariables();
    await new Promise(resolve=>setImmediate(resolve));assert.equal(pending.length,1,'same-case inventory reads share the in-flight request');
    assert.equal(entered,false,'page entry must wait for its inventory');
    pending[0]({'3d':[{name:'D',ndim:2},{name:'temp',ndim:4,nlev:3,ntimesteps:2}],timesteps_3d:2});
    await Promise.all([entering,newer]);assert.equal(entered,true);assert.deepEqual(requested,[['temp','2']]);
});

test('entry without a loaded case terminates after an empty inventory',async()=>{
    const e=environment();delete e.state.caseRevision;
    e.context.api=async()=>({error:'no active case'});
    vm.runInContext(appSource.slice(appSource.indexOf('async function loadVariables('),appSource.indexOf('// ── Dashboard')),e.context);
    vm.runInContext(appSource.slice(appSource.indexOf('async function initViz2d('),appSource.indexOf('async function updateViz2d(')),e.context);
    await e.context.initViz2d();assert.equal(e.state.variablesPending,null);
});

test('same-name variables rebuild physical layers when the case changes',async()=>{
    const e=environment({variables3d:[{name:'temp',ndim:4,nlev:3,ntimesteps:2}]}),requested=[];
    e.element('viz2d-var').options=[{value:'temp'}];
    e.context.updateViz2d=async()=>requested.push(e.element('viz2d-level').value);
    vm.runInContext(appSource.slice(appSource.indexOf('async function initViz2d('),appSource.indexOf('async function updateViz2d(')),e.context);
    vm.runInContext(appSource.slice(appSource.indexOf('async function onViz2dVarChange('),appSource.indexOf('// ── Viz2d Interaction Tools')),e.context);
    await e.context.initViz2d();assert.deepEqual(e.element('viz2d-level').options.map(o=>o.value),[2,1,0]);
    e.state.activeCasePath='B';e.state.caseRevision++;e.state.variables3d=[{name:'temp',ndim:4,nlev:5,ntimesteps:2}];
    await e.context.initViz2d();assert.deepEqual(e.element('viz2d-level').options.map(o=>o.value),[4,3,2,1,0]);
    assert.deepEqual(requested,['2','4'],'the new case must start at its real surface');
});

test('same-case refresh preserves the selected layer and tracks changed physical layer counts',async()=>{
    const e=environment({variables3d:[{name:'temp',ndim:4,nlev:3,ntimesteps:2}]}),requested=[];
    e.element('viz2d-var').options=[{value:'temp'}];
    e.context.updateViz2d=async()=>requested.push(e.element('viz2d-level').value);
    vm.runInContext(appSource.slice(appSource.indexOf('async function initViz2d('),appSource.indexOf('async function updateViz2d(')),e.context);
    vm.runInContext(appSource.slice(appSource.indexOf('async function onViz2dVarChange('),appSource.indexOf('// ── Viz2d Interaction Tools')),e.context);
    await e.context.initViz2d();e.element('viz2d-level').value='1';
    await e.context.initViz2d();assert.equal(e.element('viz2d-level').value,'1');
    e.state.variables3d[0].nlev=5;await e.context.initViz2d();
    assert.deepEqual(e.element('viz2d-level').options.map(o=>o.value),[4,3,2,1,0]);
    assert.equal(e.element('viz2d-level').value,'1','a valid same-case selection survives a metadata refresh');
    assert.deepEqual(requested,['2','1','1']);
});
