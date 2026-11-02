const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const {test}=require('node:test');
const source=fs.readFileSync('3DWET/app/static/js/viz3d.js','utf8');

const context=vm.createContext({console,window:{}});
vm.runInContext(source,context);

test('waterbody playback patch carries changed wet-cell mesh topology to Plotly',()=>{
  const previous=[{type:'mesh3d',name:'temp',meta:{waterbodyFrame:'field'},
    x:[0,1,1,0],y:[0,0,1,1],z:[0,0,0,0],i:[0,0],j:[1,2],k:[2,3],
    intensity:[1,1,1,1],customdata:[]}];
  const next=[{type:'mesh3d',name:'temp',meta:{waterbodyFrame:'field'},
    x:[2,3,3,2],y:[4,4,5,5],z:[1,1,1,1],i:[0,0],j:[1,2],k:[2,3],
    intensity:[2,2,2,2],customdata:[]}];
  const patch=context.viz3dWaterbodyRestyleGroups(previous,next);
  for(const key of ['x','y','i','j','k'])
    assert.deepEqual(JSON.parse(JSON.stringify(patch.update[key][0])),next[0][key],
      `${key} must be refreshed because equal-sized traces can represent different wet cells`);
});

test('three consecutive waterbody frames patch field colours and automatic scale together',()=>{
  const frames=[
    {intensity:[.1,.2,.3,.4],cmin:.1,cmax:.4,colorscale:[[0,'#193c68'],[1,'#55d8e8']]},
    {intensity:[.2,.3,.4,.5],cmin:.2,cmax:.5,colorscale:[[0,'#243e70'],[1,'#60d9dc']]},
    {intensity:[.3,.4,.5,.6],cmin:.3,cmax:.6,colorscale:[[0,'#314779'],[1,'#6ad9d0']]},
  ];
  const staticTrace={type:'mesh3d',name:'basin',meta:{waterbodyFrame:'bed'},z:[0,0,0,0],
    intensity:[1,1,1,1],customdata:[],opacity:1};
  const graph={data:[staticTrace,{type:'mesh3d',name:'diatoms · layer 5',meta:{scientificField:true,
    waterbodyFrame:'field',layerOrdinals:[5]},x:[0,1,1,0],y:[0,0,1,1],z:[0,0,0,0],
    i:[0,0],j:[1,2],k:[2,3],...frames[0]}]};
  const applyPlotlyUpdate=(update,indices)=>{
    for(const [property,values] of Object.entries(update))for(let position=0;position<indices.length;position++){
      // Plotly.update's outer array selects one value per trace; an array-valued
      // mesh attribute (intensity/colorscale) is the inner value for that trace.
      const value=values[position];if(value!==undefined)graph.data[indices[position]][property]=structuredClone(value);
    }
  };
  for(let frame=1;frame<=2;frame++){
    const next=graph.data.map(trace=>({...trace,meta:{...trace.meta}}));
    Object.assign(next[1],frames[frame]);
    const patch=context.viz3dWaterbodyRestyleGroups(graph.data,next);
    assert.ok(patch,'stable topology and schema should use the waterbody patch');
    const fieldPatchIndex=patch.indices.indexOf(1);
    for(const property of ['intensity','cmin','cmax','colorscale']){
      assert.deepEqual(JSON.parse(JSON.stringify(patch.update[property][fieldPatchIndex])),frames[frame][property],
        `frame ${frame} must send the new ${property} for the selected field trace`);
    }
    applyPlotlyUpdate(patch.update,patch.indices);
    for(const property of ['intensity','cmin','cmax','colorscale'])
      assert.deepEqual(graph.data[1][property],frames[frame][property],
        `the updated Plotly graph must retain frame ${frame}'s ${property}`);
  }
});

test('underside playback keeps the land framework hidden and restores its opacity above water',async()=>{
  const restyles=[];
  const context=vm.createContext({console,window:{Plotly:{restyle:async(element,update,indices)=>{
    restyles.push({update,indices});
    indices.forEach((index,position)=>{element.data[index].opacity=update.opacity[position];});
  }}},document:{getElementById:()=>null}});
  vm.runInContext(source,context);
  const [landPlane,landNetwork]=context.lakeLandTraces({xc:[0,1],yc:[0,1],
    bottom:[[NaN,NaN],[NaN,1]],dry_mask:[[true,false],[false,false]]});
  assert.ok(landNetwork.meta.landNetwork,'fixture must include the actual land wireframe trace');
  const element={data:[
    {meta:{waterbodyFrame:'bed'},opacity:1},landPlane,landNetwork,
    {meta:{scientificField:true,waterbodyFrame:'field'},opacity:.8},
  ]};
  const networkIndex=element.data.findIndex(trace=>trace.meta?.landNetwork===true);
  assert.equal(element.data[networkIndex].meta.waterbodyFrame,'land');
  const undersideCamera={eye:{z:-1},center:{z:0}};
  const surfaceCamera={eye:{z:1},center:{z:0}};

  await context.viz3dApplyUndersideMode(element,undersideCamera);

  assert.equal(element.data[0].opacity,0,'the basin is hidden below water');
  assert.equal(element.data[1].opacity,0,'the land plane is hidden below water');
  assert.equal(element.data[networkIndex].opacity,0,'the land-network trace is hidden below water');
  assert.equal(element.data[3].opacity,.8,'the scientific water field remains visible');
  assert.deepEqual(restyles[0].indices,[0,1,networkIndex],'the complete land framework must be hidden together');

  // A newly built frame starts with the network's normal .24 opacity. The
  // renderer must apply the live camera state before generating its Plotly patch.
  const nextFrame=element.data.map(trace=>({...trace,meta:{...trace.meta},
    opacity:trace.meta.landNetwork ? 0.24 : (trace.meta.waterbodyFrame==='field' ? .8 : 1)}));
  for(const trace of nextFrame)
    if(context.viz3dIsUndersideOccluder(trace))trace.opacity=context.viz3dUndersideOpacity(trace,true);
  const patch=context.viz3dWaterbodyRestyleGroups(element.data,nextFrame);
  const networkTracePosition=patch.indices.indexOf(networkIndex);
  assert.equal(patch.update.opacity[networkTracePosition],0,
    'frame 2 must patch the land-network opacity to zero');
  element.data[networkIndex].opacity=patch.update.opacity[networkTracePosition];
  assert.equal(element.data[networkIndex].opacity,0,'the second updated frame remains free of the land framework');

  await context.viz3dApplyUndersideMode(element,surfaceCamera);
  assert.equal(element.data[networkIndex].opacity,.24,'returning above water restores the original wireframe opacity');
});
