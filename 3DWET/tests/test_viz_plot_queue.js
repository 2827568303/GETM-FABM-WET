// Exercise the production renderer through an asynchronous Plotly boundary.
// Checking publish alone misses an older Plotly mutation that finishes last.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const {test}=require('node:test');
const source=fs.readFileSync('3DWET/app/static/js/viz3d.js','utf8');

function deferred(){let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b;});return {promise,resolve,reject};}
function environment(){
    const firstStarted=deferred(),firstFinished=deferred(),calls=[],published=[];
    const graph={innerHTML:'previous graph',dataset:{},_fullLayout:{scene:{camera:{eye:{x:1,y:-1,z:1}}}},data:[],on(){}};
    const sectionGraph={innerHTML:'previous section',dataset:{},_fullLayout:{scene:{}},data:[],on(){}};
    const status={dataset:{},textContent:''};
    const sectionStatus={dataset:{},textContent:''};
    const elements={'viz3d-plotly':graph,'viz3d-section-plot':sectionGraph,'viz3d-status':status,'viz3d-section-status':sectionStatus};
    const commit=(element,traces,layout)=>{element.data=traces;element.layout=layout;element._fullLayout=layout;};
    const Plotly={
        react:async(element,traces,layout)=>{
            element=typeof element==='string'?elements[element]:element;
            const call={element,traces,layout};calls.push(call);
            if(calls.length===1){firstStarted.resolve();await firstFinished.promise;}
            commit(element,traces,layout);
        },
        newPlot:()=>{throw Error('An existing graph must refresh through Plotly.react');},
    };
    const state={caseRevision:1,activeCase:'Lake A',activeCasePath:'C:/cases/A'};
    const context=vm.createContext({console,Plotly,state,URL,URLSearchParams,structuredClone,window:{Plotly,ScientificWorkspace:{publish:(kind,meta)=>published.push({kind,meta})}},
        document:{getElementById:id=>elements[id] || null},
        fetch:async url=>{
            const time=Number(new URL(url,'http://localhost').searchParams.get('time')),value=101+time*101;
            if(url.includes('/api/results/section?'))return {json:async()=>sectionData(time,value)};
            return {json:async()=>({shape:[2,2,2],xc:[0,100],yc:[0,100],bottom:[[4,8],[4,8]],sigma:[-.75,-.25],
                data:Array.from({length:2},()=>Array.from({length:2},()=>[value,value])),min:value,max:value,units:'Celsius',long_name:'Temperature'})};
        }});
    vm.runInContext(source,context);
    const render=time=>context.render3DCloud('temp',time,22,{ve:20,timeLabel:`2026-10-16 00:0${time}:00`});
    const renderSection=time=>context.renderSpatialSection('temp',time,'xz',0,{ve:20,timeLabel:`2026-10-16 00:0${time}:00`});
    return {render,renderSection,context,state,Plotly,graph,sectionGraph,status,calls,published,firstStarted,firstFinished};
}
function sectionData(time=0,value=101){return {name:'temp',time,axis:'xz',index:0,data:[[value,value],[value,value]],
    horizontal:[0,100],horizontal_edges:[-50,50,150],depth_edges:[[4,8],[2,4],[0,0]],
    bottom:[4,8],wet:[true,true],min:value,max:value,units:'Celsius',long_name:'Temperature',coordinate_units:'m',
    fixed_coordinate:0,fixed_coordinate_units:'m'};}
const flush=()=>new Promise(resolve=>setImmediate(resolve));
function assertLatest(e,frame){
    const latest=e.published.at(-1)?.meta,expected=101+frame*101;
    assert.ok(latest,'a successful latest frame must publish its metadata');
    assert.equal(latest.time,frame);
    assert.equal(latest.date,`2026-10-16 00:0${frame}:00`);
    assert.ok(e.graph.data[0]?.marker.color.every(value=>value===expected),
        'the actual graph data must match the latest published frame after all asynchronous draws finish');
    assert.match(e.graph.layout.title.text,new RegExp(latest.date),'the actual graph title must identify the same frame');
    assert.equal(e.graph._viz3dLastPlot?.timestep,frame);
    assert.equal(e.graph._viz3dMainView?.request.timestep,frame);
    assert.equal(e.graph._viz3dStatus?.phase,'ready');
}

test('a slower earlier Plotly.react cannot overwrite the actual graph after the latest frame publishes',async()=>{
    const e=environment(),old=e.render(0);await e.firstStarted.promise;
    const latest=e.render(1);await flush();
    e.firstFinished.resolve();await Promise.all([old,latest]);
    assertLatest(e,1);
});

test('rapid input during a slow draw retains only the latest queued frame and its actual graph metadata',async()=>{
    const e=environment(),old=e.render(0);await e.firstStarted.promise;
    const middle=e.render(1);await flush();
    const latest=e.render(2);await flush();
    e.firstFinished.resolve();await Promise.all([old,middle,latest]);
    assertLatest(e,2);
    assert.equal(e.calls.length,2,'an obsolete queued intermediate frame must not spend time drawing');
});

test('a rejected old Plotly draw cannot poison the later frame or its ready status',async()=>{
    const e=environment(),old=e.render(0);await e.firstStarted.promise;
    const latest=e.render(1);await flush();
    e.firstFinished.reject(Error('controlled old WebGL draw failure'));await Promise.all([old,latest]);
    assertLatest(e,1);
    assert.doesNotMatch(e.status.textContent,/controlled old WebGL draw failure/);
});

test('a queued new case replaces an unfinished old case in the actual graph without publishing old identity',async()=>{
    const e=environment(),old=e.render(0);await e.firstStarted.promise;
    e.state.activeCase='Lake B';e.state.activeCasePath='C:/cases/B';e.state.caseRevision++;
    const latest=e.render(1);await flush();
    e.firstFinished.resolve();await Promise.all([old,latest]);
    assertLatest(e,1);
    assert.equal(e.published.length,1,'the unfinished old case cannot publish any metadata');
    assert.equal(e.graph._viz3dMainView.request.key,'C:/cases/B');
    assert.equal(e.graph._viz3dMainView.request.identity.revision,2);
});

test('an unfinished main draw does not block the independent section viewport',async()=>{
    const e=environment(),main=e.render(0);await e.firstStarted.promise;
    const section=e.renderSection(0);await flush();
    const sectionDrawnWhileMainPending=e.sectionGraph.data.length;
    e.firstFinished.resolve();await Promise.all([main,section]);
    assert.equal(sectionDrawnWhileMainPending,1,'draw serialization belongs to each viewport, not a global queue');
    assert.equal(e.sectionGraph._viz3dStatus.phase,'ready');
    assertLatest(e,0);
});

test('a pending indicator mutation finishes before the latest main draw and cannot leave an old section line',async()=>{
    const e=environment(),initial=e.render(0);await e.firstStarted.promise;e.firstFinished.resolve();await initial;
    const indicatorStarted=deferred(),indicatorFinished=deferred();
    const react=e.Plotly.react;
    e.Plotly.react=async(element,traces,...args)=>{
        if(element===e.graph && traces.some(t=>t.meta?.section_indicator)){
            indicatorStarted.resolve();await indicatorFinished.promise;
        }
        return react(element,traces,...args);
    };
    const indicator=e.context.window.set3DSectionIndicator('xz',0,sectionData());await indicatorStarted.promise;
    const latest=e.render(1);await flush();
    const drawsBeforeRelease=e.calls.length;indicatorFinished.resolve();await Promise.all([indicator,latest]);
    assert.equal(drawsBeforeRelease,1,'the next main draw must await pending trace mutation');
    assertLatest(e,1);
    assert.equal(e.graph.data.some(trace=>trace.meta?.section_indicator),false,'no stale section trace survives the new main frame');
});

test('a pending main indicator cannot block the section viewport and failure does not deadlock the next main frame',async()=>{
    const e=environment(),initial=e.render(0);await e.firstStarted.promise;e.firstFinished.resolve();await initial;
    const indicatorStarted=deferred(),indicatorFinished=deferred();
    const react=e.Plotly.react;
    e.Plotly.react=async(element,traces,...args)=>{
        if(element===e.graph && traces.some(t=>t.meta?.section_indicator)){
            indicatorStarted.resolve();await indicatorFinished.promise;
        }
        return react(element,traces,...args);
    };
    const indicator=e.context.window.set3DSectionIndicator('xz',0,sectionData());await indicatorStarted.promise;
    const section=e.renderSection(0);await flush();
    const sectionDrawnWhileIndicatorPending=e.sectionGraph.data.length;
    const latest=e.render(1);await flush();indicatorFinished.reject(Error('controlled optional indicator failure'));
    await Promise.all([indicator,section,latest]);
    assert.equal(sectionDrawnWhileIndicatorPending,1,'a main-graph indicator must not stall independent section drawing');
    assertLatest(e,1);
});

test('a slower resize relayout cannot restore an older frame title after the latest actual graph finishes',async()=>{
    const e=environment(),initial=e.render(0);await e.firstStarted.promise;e.firstFinished.resolve();await initial;
    e.graph.clientWidth=800;e.graph.clientHeight=500;
    const resizeStarted=deferred(),resizeFinished=deferred();
    e.Plotly.relayout=async(element,patch)=>{resizeStarted.resolve();await resizeFinished.promise;Object.assign(element.layout,patch);};
    const resize=e.context.window.resizeScientific3D(e.graph);await resizeStarted.promise;
    const latest=e.render(1);await flush();
    resizeFinished.resolve();await Promise.all([resize,latest]);
    assertLatest(e,1);
});
