const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {test}=require('node:test');
function environment(data){const plots=[],node={innerHTML:''},Plotly={newPlot:async(e,traces,layout)=>plots.push({traces,layout})};
 const context=vm.createContext({console,Plotly,window:{Plotly},document:{getElementById:id=>id==='viz3d-plotly'?node:null},fetch:async url=>({json:async()=>String(url).includes('/api/geo/grid?display=scientific')?{shape:[data.data.length,data.data[0].length],coordinate_mode:'index',coordinate_units:'index',wetMask:data.data.map(row=>row.map(()=>true))}:data})});
 vm.runInContext(fs.readFileSync('3DWET/app/static/js/viz3d.js','utf8'),context);return {context,plots};}
test('narrow variable-height fields use explicit index domains and readable independent height',async()=>{
 const data={data:[[15.1497488,15.1497555,15.149751],[15.14975,null,15.149749]],min:15.1497488,max:15.1497555,units:'Celsius',long_name:'temperature'};
 const e=environment(data);await e.context.render2DAs3DSurface('temp',0,0,{ve:100});const p=e.plots[0],scene=p.layout.scene;
 assert.equal(scene.aspectmode,'manual');assert.ok(scene.aspectratio.z>0&&scene.aspectratio.z<3);
 assert.equal(scene.aspectratio.x/scene.aspectratio.y,3/2,'XY retain the original grid cell-count ratio');
 assert.deepEqual(Array.from(scene.xaxis.range),[-.5,2.5]);assert.deepEqual(Array.from(scene.yaxis.range),[-.5,1.5]);
 assert.deepEqual(Array.from(scene.zaxis.range),[data.min,data.max]);assert.equal(scene.zaxis.autorange,false);
 assert.equal(new Set(scene.zaxis.ticktext).size,scene.zaxis.ticktext.length);assert.ok(scene.zaxis.ticktext.length>1);
 assert.deepEqual(Array.from(p.traces[0].z),data.data.flat().filter(Number.isFinite).flatMap(v=>[v,v,v,v]),'each wet-cell vertex retains the original scalar, independent of depth VE');
 assert.equal(p.traces[0].i.length,10,'missing scalar height remains a hole');
 assert.match(scene.zaxis.title,/Celsius/);
});
test('constant and zero height fields stay flat and have one truthful scalar tick',async()=>{
 for(const value of [-15.15,0,15.15]){const data={data:[[value,value],[value,value]],min:value,max:value,units:'mg/L'};
  const e=environment(data);await e.context.render2DAs3DSurface('test',0,0);const p=e.plots[0],axis=p.layout.scene.zaxis;
  assert.equal(p.layout.scene.aspectmode,'manual');assert.deepEqual(Array.from(axis.tickvals),[value]);
  assert.ok(axis.range.every(Number.isFinite)&&axis.range[0]<=value&&axis.range[1]>=value);
  assert.ok(p.traces[0].z.flat().every(v=>v===value),'display padding cannot invent field variation');assert.match(p.layout.title.text,/常量/);
 }
});
