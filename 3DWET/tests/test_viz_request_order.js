// Production renderer regressions; fetch/Plotly are the browser boundaries only.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const {test} = require('node:test');
const source = fs.readFileSync('3DWET/app/static/js/viz3d.js', 'utf8');

function deferred() { let resolve, reject; const promise = new Promise((a,b)=>{resolve=a;reject=b;}); return {promise,resolve,reject}; }
const volume = {shape:[2,1,2],xc:[10,20],yc:[30],bottom:[[4,8]],sigma:[-.75,-.25],
    data:[[[0,-2]],[[3,null]]],min:-2,max:3,units:'mg/L',long_name:'test'};
const isoVolume={...volume,shape:[2,2,2],yc:[30,40],bottom:[[4,8],[4,8]],
    data:[[[0,-2],[0,-2]],[[3,2],[3,2]]]};
const section = {data:[[0,-2],[3,null]],horizontal:[10,20],horizontal_edges:[5,15,25],
    depth_edges:[[4,8],[2,4],[0,0]],min:-2,max:3,units:'mg/L',long_name:'test',coordinate_units:'m'};
const modes = [
    ['waterbody', c=>c.render3DWaterBody('test',1,{level:0}),volume],
    ['cloud', c=>c.render3DCloud('test',1,22),volume],
    ['isosurface', c=>c.render3DSurface('test',1,18),isoVolume],
    ['bathymetry', c=>c.renderBathymetry3D(),{depth:volume.bottom,xc:volume.xc,yc:volume.yc}],
    ['spatial section', c=>c.renderSpatialSection('test',1,'xz',0),section],
    ['variable height', c=>c.render2DAs3DSurface('test',1,0),{...volume,data:volume.data[0]}],
];
function environment() {
    const request = deferred(), json = deferred(), plots = [], guides = [], publishes=[];
    const elements = {'viz3d-plotly':{innerHTML:''},'viz3d-section-plot':{innerHTML:''},'viz3d-status':{textContent:'',dataset:{}},'viz3d-section-status':{textContent:'',dataset:{}}};
    const Plotly = {newPlot:async (el,traces,layout)=>{plots.push({traces,layout});},purge:()=>{throw Error('Loading must retain the previous graph');}};
    const context = vm.createContext({console,Promise,URL,URLSearchParams,window:{Plotly,VariableGuide:{updateValues:(...v)=>guides.push(v)},
        ScientificWorkspace:{publish:(...v)=>publishes.push(v)}},Plotly,
        state:{caseRevision:1,activeCase:'A',activeCasePath:'C:/cases/A'},
        document:{getElementById:id=>elements[id] || null},fetch:url=>String(url).includes('/api/geo/grid?display=scientific')?Promise.resolve({json:async()=>({shape:[1,2],coordinate_mode:'index',coordinate_units:'index',wetMask:[[true,true]]})}):request.promise});
    vm.runInContext(source,context);
    return {context,request,json,plots,guides,publishes,elements};
}
for (const [name,render,payload] of modes) {
    for (const field of ['caseRevision','activeCase','activeCasePath']) test(`${name}: stale ${field} cannot plot or update guidance after JSON resolves`,async()=>{
        const env = environment(), pending = render(env.context);
        env.request.resolve({json:()=>env.json.promise});
        await Promise.resolve(); await Promise.resolve();
        const before=JSON.stringify(env.elements);
        env.context.state[field]=field==='caseRevision'?2:'case B';
        env.json.resolve(payload); await pending;
        assert.equal(env.plots.length,0,'stale case payload must never reach Plotly');
        assert.equal(env.guides.length,0,'stale values must not reach VariableGuide');
        assert.equal(env.publishes.length,0,'stale values must not reach workspace metadata');
        assert.equal(JSON.stringify(env.elements),before,'stale completion must not change status/error DOM');
    });
    test(`${name}: case change before response prevents decoding and stale server error`,async()=>{
        const env=environment(), pending=render(env.context);
        const before=JSON.stringify(env.elements); let decoded=false;
        env.context.state.caseRevision++;
        env.request.resolve({json:async()=>{decoded=true;return {error:'old case server error'};}});
        await pending;
        assert.equal(decoded,false,'check case immediately after fetch, before decoding');
        assert.equal(JSON.stringify(env.elements),before);
    });
    test(`${name}: stale network rejection cannot replace the current error/status`,async()=>{
        const env=environment(),pending=render(env.context),before=JSON.stringify(env.elements);
        env.context.state.activeCasePath='C:/cases/B';env.request.reject(Error('old case failed'));
        await pending; assert.equal(JSON.stringify(env.elements),before);
    });
    test(`${name}: a delayed stale error payload cannot replace the current error/status`,async()=>{
        const env=environment(),pending=render(env.context);
        env.request.resolve({json:()=>env.json.promise});await Promise.resolve();await Promise.resolve();
        const before=JSON.stringify(env.elements);env.context.state.caseRevision++;
        env.json.resolve({error:'stale server error'});await pending;
        assert.equal(JSON.stringify(env.elements),before);assert.equal(env.guides.length,0);assert.equal(env.publishes.length,0);
    });
    test(`${name}: a case change while Plotly finishes cannot publish values or guidance`,async()=>{
        const env=environment(),started=deferred(),finished=deferred();
        env.context.Plotly.newPlot=()=>{started.resolve();return finished.promise;};
        const pending=render(env.context);env.request.resolve({json:async()=>payload});await started.promise;
        const before=JSON.stringify(env.elements);env.context.state.caseRevision++;finished.resolve();await pending;
        assert.equal(env.guides.length,0);assert.equal(env.publishes.length,0);assert.equal(JSON.stringify(env.elements),before);
    });
}
test('main view retains its last graph while loading and after a failed refresh',async()=>{
    const env=environment(), graph=env.elements['viz3d-plotly'];
    graph.innerHTML='<div class="plotly">previous valid graph</div>';
    graph._fullLayout={scene:{camera:{eye:{x:2,y:1,z:1}}}};
    const pending=env.context.render3DWaterBody('new-variable',2,{timeLabel:'2026-10-14 12:00'});
    assert.ok(graph.innerHTML.includes('previous valid graph'),'loading retains graph DOM');
    assert.match(env.elements['viz3d-status'].textContent,/加载|loading/i);
    assert.match(env.elements['viz3d-status'].textContent,/旧|previous|上一/i);
    env.request.reject(Error('offline'));await pending;
    assert.ok(graph.innerHTML.includes('previous valid graph'),'failure retains graph DOM');
    assert.match(env.elements['viz3d-status'].textContent,/offline/);
});
test('section view retains its last graph while loading and after a failed refresh',async()=>{
    const env=environment(),graph=env.elements['viz3d-section-plot'];
    graph.innerHTML='<div class="plotly">previous valid section</div>';graph._fullLayout={scene:{}};
    const pending=env.context.renderSpatialSection('test',2,'xz',1);
    assert.ok(graph.innerHTML.includes('previous valid section'));
    assert.equal(graph._viz3dStatus.phase,'loading');assert.equal(graph._viz3dStatus.stale,true);
    env.request.reject(Error('offline'));await pending;
    assert.ok(graph.innerHTML.includes('previous valid section'));assert.equal(graph._viz3dStatus.phase,'error');
});
for (const [name,render,id] of [
    ['main',c=>c.render3DWaterBody('temperature',2,{timeLabel:'2020-DOY001'}),'viz3d-plotly'],
    ['section',c=>c.renderSpatialSection('temperature',2,'xz',6),'viz3d-section-plot'],
]) test(`${name} view clears a previous case graph when the current case request fails`,async()=>{
    const env=environment(),graph=env.elements[id],purged=[];
    env.context.Plotly.purge=element=>purged.push(element);
    graph.innerHTML='<div class="plotly">case A temperature</div>';
    graph._fullLayout={scene:{}};
    graph._viz3dLastPlot={caseKey:'C:/cases/A',variable:'temperature',detail:'case A temperature · 2020-DOY001'};
    env.context.state.activeCase='B';env.context.state.activeCasePath='C:/cases/B';
    const pending=render(env.context);env.request.reject(Error('没有输出文件'));
    await pending;
    assert.deepEqual(purged,[graph]);
    assert.equal(graph._viz3dLastPlot,null);
    assert.equal(graph._viz3dStatus.phase,'error');
    assert.equal(graph._viz3dStatus.stale,false);
    assert.doesNotMatch(graph._viz3dStatus.message,/保留旧图/);
    assert.match(graph.innerHTML,/没有输出文件/);
});
test('same-case failure continues to retain its previous graph',async()=>{
    const env=environment(),graph=env.elements['viz3d-section-plot'],purged=[];
    env.context.Plotly.purge=element=>purged.push(element);
    graph.innerHTML='<div class="plotly">same case section</div>';graph._fullLayout={scene:{}};
    graph._viz3dLastPlot={caseKey:'C:/cases/A',detail:'same case section'};
    const pending=env.context.renderSpatialSection('temperature',2,'xz',6);
    env.request.reject(Error('offline'));await pending;
    assert.deepEqual(purged,[]);
    assert.ok(graph.innerHTML.includes('same case section'));
    assert.equal(graph._viz3dStatus.stale,true);
});
test('entering the 3D view for a new case clears the previous case section without a section request',async()=>{
    const env=environment(),sectionGraph=env.elements['viz3d-section-plot'],purged=[];
    env.context.Plotly.purge=element=>purged.push(element);
    const first=env.context.renderSpatialSection('temperature',2,'xz',6);
    env.request.resolve({json:async()=>section});await first;
    sectionGraph._fullLayout={scene:{}};
    sectionGraph._viz3dLastPlot={caseKey:'C:/cases/A',detail:'XZ · j=6 · 2020-DOY001'};
    sectionGraph._viz3dStatus={phase:'ready',message:'XZ · j=6 · 2020-DOY001',stale:false};
    env.elements['viz3d-section-status'].textContent='XZ · j=6 · 2020-DOY001';
    env.context.state.caseRevision++;env.context.state.activeCase='B';env.context.state.activeCasePath='C:/cases/B';
    const mainRequest=deferred();env.context.fetch=()=>mainRequest.promise;
    const entering=env.context.render3DWaterBody('temperature',0,{});
    assert.deepEqual(purged,[sectionGraph]);
    assert.equal(sectionGraph._viz3dLastPlot,null);
    assert.equal(sectionGraph._viz3dStatus.phase,'empty');
    assert.equal(sectionGraph._viz3dStatus.stale,false);
    assert.match(sectionGraph._viz3dStatus.message,/案例已切换/);
    assert.equal(env.elements['viz3d-section-status'].textContent,sectionGraph._viz3dStatus.message);
    mainRequest.reject(Error('offline'));await entering;
});
test('case switch updates an un-IDd section status element',async()=>{
    const env=environment(),sectionGraph=env.elements['viz3d-section-plot'];
    env.context.Plotly.purge=()=>{};
    const first=env.context.renderSpatialSection('temperature',2,'xz',6);
    env.request.resolve({json:async()=>section});await first;
    const orphanStatus={textContent:'XZ · j=6 · 2020-DOY001',dataset:{phase:'ready'}};
    sectionGraph._viz3dStatusElement=orphanStatus;
    delete env.elements['viz3d-section-status'];
    env.context.state.caseRevision++;env.context.state.activeCase='B';env.context.state.activeCasePath='C:/cases/B';
    const mainRequest=deferred();env.context.fetch=()=>mainRequest.promise;
    const entering=env.context.render3DWaterBody('temperature',0,{});
    assert.equal(orphanStatus.textContent,'案例已切换，请生成剖面');
    assert.equal(orphanStatus.dataset.phase,'empty');
    assert.equal(orphanStatus.id,'viz3d-section-status');
    mainRequest.reject(Error('offline'));await entering;
});
