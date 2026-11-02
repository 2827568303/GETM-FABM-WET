const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {test}=require('node:test');
const source=fs.readFileSync('3DWET/app/static/js/viz3d.js','utf8');
const cube={shape:[2,2,2],xc:[100,200],yc:[1000,1100],bottom:[[4,8],[4,8]],sigma:[-1,0],
 data:[[[0,1],[0,1]],[[0,1],[0,1]]],min:0,max:1,units:'mg/L',long_name:'analytic x field'};
function env(payload){
 const plots=[],published=[],status={textContent:'',dataset:{}},container={innerHTML:'',dataset:{}};
 const Plotly={newPlot:async(el,traces,layout)=>plots.push({traces,layout})};
 const context=vm.createContext({console,URL,URLSearchParams,Plotly,window:{Plotly,ScientificWorkspace:{publish:(kind,meta)=>published.push(meta)}},
  document:{getElementById:id=>id==='viz3d-status'?status:container},fetch:async()=>({json:async()=>payload})});
 vm.runInContext(source,context);return {context,plots,published,status};
}
test('actual isosurface renderer submits nonempty physical meshes with exact thresholds and depth hover',async()=>{
 const e=env(cube);await e.context.render3DSurface('test',0,18,{ve:20});
 assert.equal(e.plots.length,1);assert.equal(e.published.length,1);
 const traces=e.plots[0].traces;
 assert.equal(traces.length,2);
 for(const [n,trace] of traces.entries()){
  const iso=n===0?.4:.7;
  assert.equal(trace.type,'mesh3d','sigma geometry must not use the Cartesian-only Plotly isosurface primitive');
  assert.ok(trace.i.length>0,'success requires actual surface triangles');
  assert.ok(trace.x.every(x=>Math.abs(x-(100+100*iso))<1e-10));
  assert.ok(trace.intensity.every(v=>v===iso));
  assert.ok(trace.z.every((z,i)=>Math.abs(trace.customdata[i]+z/20)<1e-10));
  assert.match(trace.hovertemplate,/%\{intensity/);assert.match(trace.hovertemplate,/mg\/L/);
 }
 assert.equal(traces.at(-1).showscale,true);
});
test('a sampled volume without complete wet cells reports no surface instead of false success',async()=>{
 const e=env({...cube,bottom:[[4,0],[4,0]]});await e.context.render3DSurface('test',0);
 assert.equal(e.plots.length,0);assert.equal(e.published.length,0);
 assert.match(e.status.textContent,/未形成|no.*surface/i);
});
