const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const {test}=require('node:test');

const source=fs.readFileSync('3DWET/app/static/js/viz3d.js','utf8');
const payload={shape:[2,1,2],xc:[0,100],yc:[0],bottom:[[4,8]],sigma:[-.75,-.25],
  data:[[[0,-2]],[[3,2]]],min:-2,max:3,units:'mg/L',long_name:'test',
  layer_indices:[0,1],total_layers:2};
const pause=ms=>new Promise(resolve=>setTimeout(resolve,ms));

function env({staticGeometry=false}={}){
  const fetched=[],plots=[],perfStages=[],urls=[],translationCalls=[];
  const container={id:'viz3d-plotly',innerHTML:'',dataset:{},clientWidth:800,clientHeight:600,
    parentNode:null,on(){}};
  const slider={max:'2'},playStart={value:'0'},playEnd={value:'2'};
  const Plotly={
    newPlot:async(element,traces,layout)=>{const plot={method:'newPlot',traces,layout};plots.push(plot);await pause(60);element._fullLayout={};plot.drawFinishedAt=Date.now();},
    react:async(element,traces,layout)=>{const plot={method:'react',traces,layout};plots.push(plot);await pause(60);plot.drawFinishedAt=Date.now();},
  };
  const PlaybackPerformance={begin:(kind,frame)=>({kind,frame}),stage:(ticket,name,ms)=>perfStages.push({frame:ticket?.frame,name,ms}),finish(){}};
  const framePayload={...payload,dry_mask:[[false,true]],...(staticGeometry?{static_geometry_key:'geometry-1'}:{})};
  const context=vm.createContext({console,Plotly,URL,URLSearchParams,structuredClone,state:{activeCase:'lake',activeCasePath:'/lake',caseRevision:1,outputRevision:4},window:{Plotly,PlaybackPerformance,
    StudioI18n:{locale:()=> 'zh-CN',t:value=>{translationCalls.push(value);return value;}},
    translateChartLabels:wrapper=>translationCalls.push(wrapper.text),
    ScientificWorkspace:{isPlaying:kind=>kind==='viz3d'}},
    document:{getElementById:id=>id==='viz3d-plotly'?container:id==='viz3d-time-slider'?slider:id==='viz3d-play-start'?playStart:id==='viz3d-play-end'?playEnd:null},
    fetch:async url=>{
      const time=Number(new URL(url,'http://localhost').searchParams.get('time'));
      fetched.push({time,at:Date.now(),url});urls.push(url);
      await pause(25);
      return {json:async()=>({...framePayload,timestep:time})};
    }});
  vm.runInContext(source,context);
  return {context,fetched,plots,playStart,playEnd,perfStages,urls,translationCalls,payload:framePayload};
}

test('3D playback requests the next output during the current Plotly draw and reuses it once',async()=>{
  const e=env();
  e.playEnd.value='8';
  await e.context.render3DWaterBody('temp',0,{target:8,level:0,caseKey:'lake',showBedSurface:true});
  assert.ok(e.fetched.some(item=>item.time===1),'frame 1 should be prefetched during frame 0 rendering');
  assert.ok(e.fetched.some(item=>item.time===2),'frame 2 should be prefetched alongside frame 1 to cover main-thread stalls');
  assert.ok(e.fetched.some(item=>item.time===3),'frame 3 should extend the lookahead across slow request and decode stages');
  assert.ok(e.fetched.some(item=>item.time===4),'four future frames should be buffered to cover the measured 3D request/decode latency');
  assert.equal(e.fetched.filter(item=>item.time>0).length,4,'the playback cache must remain bounded to four future output frames');
  const prefetch=e.fetched.find(item=>item.time===1);
  assert.ok(prefetch.at<e.plots[0].drawFinishedAt,'prefetch should start before the current Plotly draw settles');
  assert.ok(e.fetched.find(item=>item.time===2).at<e.plots[0].drawFinishedAt,'the bounded second lookahead starts during the same draw');

  await e.context.render3DWaterBody('temp',1,{target:8,level:0,caseKey:'lake',showBedSurface:true});
  assert.equal(e.fetched.filter(item=>item.time===1).length,1,'the prefetched output must satisfy frame 1 without a duplicate request');
  assert.equal(e.plots[1].method,'react');
  await e.context.render3DWaterBody('temp',2,{target:8,level:0,caseKey:'lake'});
  assert.equal(e.fetched.filter(item=>item.time===2).length,1,'the second prefetched output is consumed without duplicate work');
});

test('waterbody playback requests compact vertical geometry and preserves the synchronization warning',async()=>{
  const e=env();
  e.context.window.ScientificWorkspace.isPlaying=()=>false;
  e.payload.valid_geometry=[[true,false]];
  e.payload.surface_synchronized=[[false,false]];
  await e.context.render3DWaterBody('temp',0,{target:96,level:0,caseKey:'lake',overlay:true});
  assert.match(e.urls[0],/[?&]waterbody_compact=1(?:&|$)/,
    'single-layer waterbody playback should ask the API to omit unconsumed dynamic geometry arrays');
  assert.equal(e.context.lakeDepthSource({surface_synchronized:[[false,false]],valid_geometry:[[false,false]]})
    .includes('二维水位更新时刻不同'),false,
    'a mismatch only on invalid geometry must not create the synchronization warning');
  assert.equal(e.context.lakeDepthSource({surface_sync_mismatch:true})
    .includes('二维水位更新时刻不同'),true,
    'the compact mismatch summary must retain the warning when a valid wet cell is unsynchronized');
});

test('compact frame20-style payload preserves continuous waterbody colors and has no mesh-line overlay',async()=>{
  const makeFrame=()=>({
    ...payload,
    shape:[2,1,2],full_shape:[2,1,2],bottom:[[4,8]],water_depth:[[4,8]],
    data:[[[5.514081,5.86819]],[[5.6,5.7]]],
    min:5.514081,max:5.86819,valid_geometry:[[true,true]],
    elevation:[[[1,2]],[[3,4]]],depth:[[[3,6]],[[1,2]]],
    surface_synchronized:[[false,true]],
  });
  const full=env(),compact=env();
  full.context.window.ScientificWorkspace.isPlaying=()=>false;
  compact.context.window.ScientificWorkspace.isPlaying=()=>false;
  Object.assign(full.payload,makeFrame());
  Object.assign(compact.payload,makeFrame());
  for(const key of ['depth','surface_synchronized','surface_elevation',
    'barotropic_surface_elevation','surface_difference'])delete compact.payload[key];
  compact.payload.surface_sync_mismatch=true;
  await full.context.render3DWaterBody('temp',20,{target:96,level:0,caseKey:'lake',overlay:true,meshMode:'continuous'});
  await compact.context.render3DWaterBody('temp',20,{target:96,level:0,caseKey:'lake',overlay:true,meshMode:'continuous'});
  const fullPlot=full.plots[0],compactPlot=compact.plots[0];
  const fullField=fullPlot.traces.find(trace=>trace.meta?.scientificField);
  const compactField=compactPlot.traces.find(trace=>trace.meta?.scientificField);
  assert.ok(fullField&&compactField,'both responses should produce the scientific field mesh');
  for(const key of ['x','y','z','i','j','k','intensity','customdata','cmin','cmax','colorscale'])
    assert.deepEqual(JSON.parse(JSON.stringify(compactField[key])),JSON.parse(JSON.stringify(fullField[key])),
      `compact response must preserve field mesh ${key}`);
  assert.equal(compactPlot.layout.title.text,fullPlot.layout.title.text,
    'the summarized geometry-sync status should preserve the full-response label');
  assert.equal(compactPlot.traces.some(trace=>trace.meta?.networkMode),false,
    'continuous mode has no explicitly enabled display-mesh/network line overlay');
});

test('3D consecutive frames reuse cached shoreline and land traces only while case, output, and topology identity match',async()=>{
  const e=env({staticGeometry:true});
  await e.context.render3DWaterBody('temp',0,{target:8,level:0,caseKey:'lake',showBedSurface:true});
  const first=e.plots[0].traces;
  const shoreline=first.find(trace=>trace.meta?.shoreline);
  const land=first.find(trace=>trace.meta?.landPlane);
  assert.ok(shoreline&&land,'fixture must include a shoreline and a known-land trace');
  await e.context.render3DWaterBody('temp',1,{target:8,level:0,caseKey:'lake',showBedSurface:true});
  const second=e.plots[1].traces;
  assert.strictEqual(second.find(trace=>trace.meta?.shoreline).x,shoreline.x,
    'static shoreline coordinates should be reused instead of smoothed and allocated again');
  assert.strictEqual(second.find(trace=>trace.meta?.landPlane).x,land.x,
    'static land mesh should be reused instead of rebuilt on every output frame');

  e.context.state.caseRevision=2;
  await e.context.render3DWaterBody('temp',2,{target:8,level:0,caseKey:'lake'});
  assert.notStrictEqual(e.plots[2].traces.find(trace=>trace.meta?.shoreline).x,shoreline.x,
    'a changed case revision must invalidate static trace reuse');
  e.context.state.outputRevision=5;
  await e.context.render3DWaterBody('temp',3,{target:8,level:0,caseKey:'lake'});
  assert.notStrictEqual(e.plots[3].traces.find(trace=>trace.meta?.shoreline).x,
    e.plots[2].traces.find(trace=>trace.meta?.shoreline).x,
    'a changed output revision must invalidate static trace reuse');
  e.payload.static_geometry_key='geometry-2';
  await e.context.render3DWaterBody('temp',4,{target:8,level:0,caseKey:'lake'});
  assert.notStrictEqual(e.plots[4].traces.find(trace=>trace.meta?.shoreline).x,
    e.plots[3].traces.find(trace=>trace.meta?.shoreline).x,
    'a changed static topology key must invalidate static trace reuse');
  await e.context.render3DWaterBody('chlorophyll',5,{target:8,level:0,caseKey:'lake'});
  assert.notStrictEqual(e.plots[5].traces.find(trace=>trace.meta?.shoreline).x,
    e.plots[4].traces.find(trace=>trace.meta?.shoreline).x,
    'a changed variable must not reuse traces compiled for another view');
  await e.context.render3DWaterBody('chlorophyll',6,{target:8,level:0,caseKey:'lake',meshMode:'triangles'});
  assert.notStrictEqual(e.plots[6].traces.find(trace=>trace.meta?.shoreline).x,
    e.plots[5].traces.find(trace=>trace.meta?.shoreline).x,
    'a changed mesh mode must not reuse a trace bundle from a different view mode');
});

test('3D playback does not prefetch past the selected playback end',async()=>{
  const e=env();e.playEnd.value='1';
  await e.context.render3DWaterBody('temp',1,{target:8,level:0,caseKey:'lake'});
  await pause(30);
  assert.deepEqual(e.fetched.map(item=>item.time),[1]);
});

test('3D playback does not reuse a prefetched frame after the same case produces a new output revision',async()=>{
  const e=env();
  await e.context.render3DWaterBody('temp',0,{target:8,level:0,caseKey:'lake'});
  e.context.state.outputRevision=5;
  await e.context.render3DWaterBody('temp',1,{target:8,level:0,caseKey:'lake'});
  assert.equal(e.fetched.filter(item=>item.time===1).length,2,
    'same case/variable/layer must fetch the current run instead of consuming its previous-run prefetch');
});

test('3D telemetry reports serialized Plotly queue wait separately from synchronous frame assembly',async()=>{
  const e=env();
  const first=e.context.render3DWaterBody('temp',0,{target:8,level:0,caseKey:'lake'});
  await pause(35); // frame 0 is inside the deliberately slow Plotly draw
  const second=e.context.render3DWaterBody('temp',1,{target:8,level:0,caseKey:'lake'});
  await Promise.all([first,second]);
  const queue=e.perfStages.find(stage=>stage.frame===1&&stage.name==='queueWait');
  assert.ok(queue && queue.ms>=20,'time waiting behind frame 0 must have its own queueWait measurement');
  const assemble=e.perfStages.find(stage=>stage.frame===1&&stage.name==='assemble');
  assert.ok(assemble && assemble.ms<queue.ms,'queue wait must not inflate synchronous assembly time');
});

test('single-layer waterbody playback requests only its selected physical layer',async()=>{
  const e=env();
  await e.context.render3DWaterBody('temp',0,{target:8,level:1,caseKey:'lake',stack:false});
  assert.match(e.urls[0],/[?&]level=1(?:&|$)/);
  assert.match(e.urls[0],/[?&]layer_only=1(?:&|$)/,
    'non-stack waterbody playback should not transfer unrendered vertical layers');
});

test('stacked waterbody view keeps every physical layer in its API request',async()=>{
  const e=env();
  await e.context.render3DWaterBody('temp',0,{target:8,level:1,caseKey:'lake',stack:true});
  assert.match(e.urls[0],/[?&]level=1(?:&|$)/);
  assert.doesNotMatch(e.urls[0],/[?&]layer_only=1(?:&|$)/,
    'stacked rendering requires the requested vertical range');
});

test('default waterbody surface selects the API surface ordinal without transferring other layers',async()=>{
  const e=env();
  await e.context.render3DWaterBody('temp',0,{target:8,caseKey:'lake',stack:false});
  assert.match(e.urls[0],/[?&]level=-1(?:&|$)/);
  assert.match(e.urls[0],/[?&]layer_only=1(?:&|$)/);
});

test('switching from single layer to stack does not reuse single-layer geometry metadata',async()=>{
  const e=env({staticGeometry:true});
  await e.context.render3DWaterBody('temp',0,{target:8,level:1,caseKey:'lake',stack:false});
  await e.context.render3DWaterBody('temp',0,{target:8,level:1,caseKey:'lake',stack:true});
  const stackRequest=e.urls.find(url=>/[?&]time=0(?:&|$)/.test(url)&&/[?&]level=1(?:&|$)/.test(url)&&!/[?&]layer_only=1(?:&|$)/.test(url));
  assert.ok(stackRequest,'stack playback request should be distinguishable from its background lookahead');
  assert.doesNotMatch(stackRequest,/static_key=/,
    'a one-layer cached payload cannot describe the subsequent stacked response');
});

test('repeated waterbody labels reuse translation output across adjacent frames',async()=>{
  const e=env();
  await e.context.render3DWaterBody('temp',0,{target:8,level:0,caseKey:'lake',showBedSurface:true});
  const afterFirst=e.translationCalls.filter(value=>value==='湖盆水深').length;
  assert.ok(afterFirst>0,'first frame must translate the static bathymetry trace label');
  await e.context.render3DWaterBody('temp',1,{target:8,level:0,caseKey:'lake',showBedSurface:true});
  assert.equal(e.translationCalls.filter(value=>value==='湖盆水深').length,afterFirst,
    'the same locale/case static label should not be translated again on every frame');
});

test('3D Plotly preparation reports translation, layout, and schema costs separately',async()=>{
  const e=env();
  await e.context.render3DWaterBody('temp',0,{target:8,level:0,caseKey:'lake'});
  for(const name of ['plotTranslate','plotLayout','plotSchema'])
    assert.ok(e.perfStages.some(stage=>stage.frame===0&&stage.name===name),`${name} stage should identify plot preparation cost`);
});
