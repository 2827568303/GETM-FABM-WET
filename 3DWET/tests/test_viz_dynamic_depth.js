const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {test}=require('node:test');
const source=fs.readFileSync('3DWET/app/static/js/viz3d.js','utf8');
const payload={shape:[2,2,2],xc:[0,100],yc:[0,100],bottom:[[10,8],[10,8]],
 water_depth:[[12,8],[12,8]],surface_elevation:[[2,0],[2,0]],sigma:[-.75,-.25],
 depth:[[[10.5,7],[10.5,7]],[[4.5,3],[4.5,3]]],
 elevation:[[[-8.5,-7],[-8.5,-7]],[[-2.5,-3],[-2.5,-3]]],
 depth_source:'hn+zc',depth_position:'center',depth_reference:'below instantaneous water surface',
 data:[[[0,1],[0,1]],[[2,3],[2,3]]],min:0,max:3,units:'Celsius'};
function env(data=payload,fetcher=null){
 const plots=[],graph={innerHTML:'',dataset:{},on(){}},status={dataset:{},textContent:''};
 const Plotly={newPlot:async(_,traces,layout)=>plots.push({traces,layout})};
 const context=vm.createContext({console,URL,URLSearchParams,structuredClone,window:{Plotly},Plotly,
  document:{getElementById:id=>id==='viz3d-status'?status:graph},fetch:fetcher|| (async()=>({json:async()=>data}))});
 vm.runInContext(source,context);return {context,plots,status};
}
test('physical volume samples use actual layer depths rather than static sigma',()=>{
 const e=env(),s=e.context.lakeVolumeSamples(payload,2);
 assert.deepEqual(Array.from(s.z),[-21,-14,-21,-14,-9,-6,-9,-6]);
 const next=structuredClone(payload);next.depth[0][0][0]=11;
 assert.equal(e.context.lakeVolumeSamples(next,2).z[0],-22,'new frame cannot reuse old positions');
});
test('waterbody uses dynamic total depth and native centre readouts at its displayed corners',async()=>{
 const e=env();await e.context.render3DWaterBody('temp',1,{level:0,ve:2});
 const field=e.plots[0].traces.find(trace=>trace.meta?.scientificField===true);
 assert.equal(field.z[0],-21);assert.equal(field.customdata[0][0],10.5);
 assert.equal(field.customdata[0][1],-8.5);
 assert.match(field.hovertemplate,/单元中心|cell centre/i);
 assert.match(e.status.textContent,/hn\+zc/);
 assert.equal(Math.min(...e.plots[0].layout.scene.zaxis.range),-24,'bed range uses actual water-column depth');
});
test('point cloud and isosurface share the same actual vertical grid',async()=>{
 const e=env();await e.context.render3DCloud('temp',1,26,{ve:2});
 assert.deepEqual(Array.from(e.plots[0].traces[0].z),[-21,-14,-21,-14,-9,-6,-9,-6]);
 assert.match(e.status.textContent,/hn\+zc/);
 const mesh=e.context.buildStructuredIsosurface(payload,.5,2);
 assert.ok(mesh.i.length);
 assert.ok(mesh.z.every(z=>z<=-17.5 && z>=-21),'iso intersections use native positions on the lower physical layer');
});
test('unavailable physical geometry cannot fall back to made-up layer positions',async()=>{
 for(const mode of ['render3DWaterBody','render3DCloud','render3DSurface']){
  const e=env({...payload,depth:null,depth_geometry_error:'缺少实际层厚 hn 或显式 sigma 坐标'});
  await e.context[mode]('temp',0);
  assert.equal(e.plots.length,0,mode);assert.match(e.status.textContent,/sigma|hn/);
 }
});
test('native depth remains usable when unused sigma coordinates are unavailable',async()=>{
 const data={...payload,sigma:[-.75,null]},e=env(data);
 const samples=e.context.lakeVolumeSamples(data,2);
 assert.equal(samples.z[4],-9);assert.equal(samples.values[4],2);
 await e.context.render3DWaterBody('temp',0,{level:1,ve:2});
 assert.equal(e.plots.length,1);assert.equal(e.plots[0].traces.find(trace=>trace.meta?.scientificField===true).z[0],-9);
});
test('hover and plot axes distinguish model elevation and current or static depth datum',async()=>{
 for(const mode of ['render3DWaterBody','render3DCloud']){
  const e=env();await e.context[mode]('temp',0);
  const trace=mode==='render3DCloud'?e.plots[0].traces[0]:e.plots[0].traces.find(item=>item.meta?.scientificField===true);
  assert.match(trace.hovertemplate,/高程|elevation/i);
  assert.match(e.plots[0].layout.scene.zaxis.title,/水深|Depth/i);
  assert.ok(e.plots[0].layout.scene.zaxis.title.length<22);
  assert.match(e.plots[0].layout.title.text,/当前水面|instantaneous/i);
 }
 const e=env({...payload,depth_reference:'below static bathymetric surface'});
 await e.context.render3DWaterBody('temp',0);
 assert.match(e.plots[0].layout.scene.zaxis.title,/水深|Depth/i);
 assert.match(e.plots[0].layout.title.text,/静态水面|static/i);
});
test('static bathymetry preview does not require missing result layer geometry',async()=>{
 const e=env({...payload,depth:null,depth_geometry_error:'缺少实际层厚 hn 或显式 sigma 坐标'});
 await e.context.render3DWaterBody('temp',0,{overlay:false});
 assert.equal(e.plots.length,1);
 assert.match(e.plots[0].layout.scene.zaxis.title,/水深|Depth/i);
 assert.match(e.plots[0].layout.title.text,/静态水面|static/i);
 const bad=env({...payload,depth_geometry_error:'bathymetry 单位必须为米',bathymetry_geometry_error:'bathymetry 单位必须为米'});
 await bad.context.render3DWaterBody('temp',0,{overlay:false});
 assert.equal(bad.plots.length,0,'static preview still cannot fabricate bathymetry units');
});
test('missing dynamic output falls back to a clearly labeled static waterbody preview',async()=>{
 const grid={nx:2,ny:2,xc:[0,100],yc:[0,100],depth:[[4,8],[12,0]],dry_mask:[[false,false],[false,true]]};
 const urls=[];
 const e=env(payload,async url=>{
  urls.push(String(url));
  return {json:async()=>String(url).includes('/api/results/3d_surface')?{error:'没有3D输出文件'}:grid};
 });
 await e.context.render3DWaterBody('temp',0,{level:0,overlay:true});
 assert.ok(urls.some(url=>url.includes('/api/results/3d_surface')),'the requested dynamic output is checked first');
 assert.ok(urls.some(url=>url==='/api/geo/grid'),'static bathymetry is fetched when dynamic output is unavailable');
 assert.equal(e.plots.length,1,'the static lake preview renders instead of leaving the 3D canvas empty');
 assert.ok(!e.plots[0].traces.some(trace=>trace.meta?.waterbodyFrame==='bed'),
  'the static fallback keeps the lake bed hidden by default');
 assert.ok(e.plots[0].traces.some(trace=>trace.meta?.waterbodyFrame==='wall'),
  'wet-grid sidewalls retain the visible water volume');
 const water=e.plots[0].traces.find(trace=>trace.meta?.waterbodyFrame==='surface');
 assert.ok(water&&water.opacity===.58,'the labeled static preview uses the shared readable water-surface opacity');
 assert.ok(e.plots[0].traces.some(trace=>trace.meta?.shoreline),'the wet-mask edge remains explicitly represented');
 assert.match(e.status.textContent,/无动态输出|no dynamic output/i);
 assert.match(e.status.textContent,/湿网格|wet.mask/i);
});
test('isosurface model elevations follow the same physical interpolation as its vertices',()=>{
 const e=env(),mesh=e.context.buildStructuredIsosurface(payload,.5,2);
 assert.ok(mesh.i.length);assert.equal(mesh.elevation.length,mesh.x.length);
 mesh.elevation.forEach((height,n)=>assert.ok(Math.abs(height-(2-2*mesh.x[n]/100+mesh.z[n]/2))<1e-12));
});
