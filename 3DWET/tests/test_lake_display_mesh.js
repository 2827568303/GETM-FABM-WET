const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {test}=require('node:test');
const source=fs.readFileSync('3DWET/app/static/js/viz3d.js','utf8');
test('the 3D renderer asset URL cache-bust tracks the v173 renderer source',()=>{
 const html=fs.readFileSync('3DWET/app/templates/index.html','utf8');
 const match=html.match(/\/static\/js\/viz3d\.js\?v=(\d+)/);
 assert.ok(match,'the index template must include the 3D renderer');
 assert.equal(Number(match[1]),173,'renderer changes must invalidate cached v172 assets');
});
function fixtureTopology(data){
 if(!data||Object.prototype.hasOwnProperty.call(data,'display_topology'))return data;
 const bottom=data.bottom||data.depth,rows=bottom?.length||data.wetMask?.length||data.shape?.[1],cols=bottom?.[0]?.length||data.wetMask?.[0]?.length||data.shape?.[2];
 if(!Number.isInteger(rows)||!Number.isInteger(cols)||rows<1||cols<1)return data;
 const wetMask=Array.from({length:rows},(_,j)=>Array.from({length:cols},(_,i)=>{
  const value=bottom?.[j]?.[i];return data.wetMask?.[j]?.[i]===true||(Number.isFinite(value)&&value>0&&data.valid_geometry?.[j]?.[i]!==false);
 }));
 const landMask=Array.from({length:rows},(_,j)=>Array.from({length:cols},(_,i)=>{
  const value=bottom?.[j]?.[i];return data.dry_mask?.[j]?.[i]===true||(Number.isFinite(value)&&value<=0);
 }));
 const cellStatus=Array.from({length:rows},(_,j)=>Array.from({length:cols},(_,i)=>wetMask[j][i]?'wet':landMask[j][i]?'dry':Number.isFinite(bottom?.[j]?.[i])?'mixed':'unknown'));
 const axes=(values,count)=>{const axis=Array.isArray(values)&&values.length===count?values:Array.from({length:count},(_,i)=>i);if(count===1)return [axis[0]-.5,axis[0]+.5];const result=[axis[0]-(axis[1]-axis[0])/2];for(let i=1;i<count;i++)result.push((axis[i-1]+axis[i])/2);result.push(axis[count-1]+(axis[count-1]-axis[count-2])/2);return result;};
 const wallSides=cellStatus.map((row,j)=>row.map((status,i)=>[[-1,0],[0,1],[1,0],[0,-1]].map(([dj,di])=>status==='wet'&&cellStatus[j+dj]?.[i+di]==='dry')));
 const shape=Array.isArray(data.shape)&&(data.shape.length===2||data.shape.length===3)?data.shape:[1,rows,cols];
 return {...data,shape,bottom:bottom||wetMask.map(row=>row.map(value=>value?1:0)),display_topology:{
  contract:'sampled-wet-topology-v1',source_shape:[rows,cols],x_indices:Array.from({length:cols},(_,i)=>i),y_indices:Array.from({length:rows},(_,i)=>i),sampling_stride:[1,1,1],
  grid_hash:'sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',mask_cells_examined:rows*cols,
  x_edges:axes(data.xc,cols),y_edges:axes(data.yc,rows),cell_status:cellStatus,wet_mask:wetMask,land_mask:landMask,wall_sides:wallSides,mixed_or_unknown_cells:cellStatus.flat().filter(value=>value==='mixed'||value==='unknown').length}};
}
function env(data,geometry){let currentData=data;const plots=[],graph={innerHTML:'',dataset:{},on(){}},status={dataset:{},textContent:''};
 const Plotly={newPlot:async(_,traces,layout)=>plots.push({traces,layout})};
 const context=vm.createContext({console,URL,URLSearchParams,window:{Plotly,location:{search:''}},Plotly,document:{getElementById:id=>id==='viz3d-status'?status:graph},fetch:async url=>({json:async()=>fixtureTopology(String(url).includes('/api/geo/grid')&&geometry?geometry:currentData)})});
 vm.runInContext(source,context);return {context,plots,status,graph,setData:value=>{currentData=value;}};}
const plain=x=>JSON.parse(JSON.stringify(x));
test('static bathymetry blends display depth at wet corners but retains native cell hover depth',()=>{
 const c=env().context;
 const surface={x:[0,1,1,0],y:[0,0,1,1],cell:[[0,0],[0,0],[0,0],[0,0]]};
 const projection=c.lakeSurfaceDepthProjection(surface,{bottom:[[2,6],[10,0]]});
 assert.deepEqual(plain(projection.intensity),[2,4,6,6],
  'shared corners average only adjacent wet cells, without smoothing the wet footprint');
 assert.deepEqual(plain(projection.customdata),[2,2,2,2],
  'hover continues to report the native depth of the originating cell');
});
test('trace audit labels describe the just-rendered frame and vertical exaggeration',async()=>{
 const data={shape:[1,1,1],xc:[0],yc:[0],bottom:[[4]],water_depth:[[4]],
  depth:[[[2]]],sigma:[-.5],data:[[[1]]],min:1,max:1};
 const e=env(data),panel={_viz3dTraceAuditOutput:{textContent:''}},getElement=e.context.document.getElementById;
 e.context.window.location.search='?viz3d-trace-audit=1';
 e.context.document.getElementById=id=>id==='viz3d-trace-audit'?panel:getElement(id);
 e.context.window.Plotly.newPlot=async(_,traces,layout)=>{
  e.graph._fullData=traces;e.graph._fullLayout=layout;
 };
 await e.context.render3DWaterBody('temp',0,{level:0,ve:50});
 await e.context.render3DWaterBody('temp',19,{level:0,ve:200});
 assert.equal(panel._viz3dTraceAuditReport.selection.frame,19,'audit must label the current frame, not frame 0');
 assert.equal(panel._viz3dTraceAuditReport.selection.ve,200,'audit must label the current VE, not 50');
});
for(const [name,bottom] of Object.entries({island:[[5,5,5],[5,0,5],[5,5,5]],diagonal:[[5,0,0],[0,5,0],[0,0,5]],channel:[[0,5,0],[0,5,0],[5,5,5]]})){
 test(`${name}: display surface faces and network lines stay inside wet cells without mutating geometry`,()=>{
  const c=env().context,g=c.buildLakeGeometry([0,1,2],[0,1,2],bottom),before=plain(g);
  for(let t=0;t<g.floor.i.length;t++){
   const ids=[g.floor.i[t],g.floor.j[t],g.floor.k[t]],cell=g.floor.cell[ids[0]];
   assert.ok(bottom[cell[1]][cell[0]]>0);for(const q of ids)assert.deepEqual(plain(g.floor.cell[q]),plain(cell));
  }
  const orth=c.buildLakeGrid(g,{mode:'orthogonal',density:1}),facets=c.buildLakeGrid(g,{mode:'triangles',density:1});
  for(let q=0;q<orth.x.length;q+=3)assert.ok(orth.x[q]===orth.x[q+1]||orth.y[q]===orth.y[q+1]);
  assert.ok(facets.x.length>orth.x.length,'triangular network adds wet-cell diagonals');
  assert.equal(c.buildLakeGrid(g,{mode:'hidden'}).x.length,0);assert.equal(c.buildLakeGrid(g,{mode:'continuous'}).x.length,0);
  assert.deepEqual(plain(g),before,'overlay mode cannot mutate solver coordinates or triangles');
 });
}
test('sampled geometry draws only fully wet native blocks and uses verified dry neighbors for walls and land',()=>{
 const c=env().context,topology={
  contract:'sampled-wet-topology-v1',source_shape:[1,17],x_indices:[0,8,16],y_indices:[0],
  sampling_stride:[1,8],grid_hash:'sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',mask_cells_examined:17,
  x_edges:[-.5,7.5,15.5,16.5],y_edges:[-.5,.5],
  cell_status:[['mixed','wet','dry']],wet_mask:[[false,true,false]],land_mask:[[false,false,true]],
  wall_sides:[[[false,false,false,false],[false,true,false,false],[false,false,false,false]]],
  mixed_or_unknown_cells:1
 };
 const g=c.buildLakeGeometry([0,8,16],[0],[[5,5,0]],1,topology);
 assert.equal(g.floor.i.length,2,'mixed sampled blocks cannot become water faces');
 assert.deepEqual(plain(g.floor.cell),[[1,0],[1,0],[1,0],[1,0]]);
 assert.equal(g.walls.i.length,2,'only the contract-approved wet-to-dry interface gets a vertical wall');
 assert.deepEqual(plain(g.shoreline.x),[15.5,15.5,null]);
 const land=c.buildLakeLand({xc:[0,8,16],yc:[0],dry_mask:[[false,false,true]],display_topology:topology});
 assert.equal(land.i.length,2,'only a fully dry coarse block is presented as land');
 assert.deepEqual(plain(land.x),[15.5,16.5,16.5,15.5]);
 assert.equal(g.displayTopology.mixed_or_unknown_cells,1);
});
test('invalid sampled topology is rejected and never falls back to sampled-only quads',async()=>{
 const c=env().context,valid={
  contract:'sampled-wet-topology-v1',source_shape:[1,17],x_indices:[0,8,16],y_indices:[0],
  grid_hash:'sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',mask_cells_examined:17,
  x_edges:[-.5,7.5,15.5,16.5],y_edges:[-.5,.5],cell_status:[['mixed','wet','dry']],
  wet_mask:[[false,true,false]],land_mask:[[false,false,true]],wall_sides:[[[false,false,false,false],[false,true,false,false],[false,false,false,false]]]
 };
 assert.equal(c.buildLakeGeometry([0,8,16],[0],[[5,5,0]],1,{...valid,wall_sides:[]}),null);
 const data={shape:[1,1,3],full_shape:[1,1,17],sampling_stride:[1,1,8],x:[0,8,16],y:[0],
  xc:[0,8,16],yc:[0],bottom:[[5,5,5]],water_depth:[[5,5,5]],data:[[[1,2,3]]],sigma:[-.5],
  display_topology:null,depth:[[[2,2,2]]],valid_geometry:[[true,true,true]],min:1,max:3};
 for(const render of [
  c=>c.render3DWaterBody('temp',0,{level:0}),
  c=>c.render3DCloud('temp',0,8),
  c=>c.render3DSurface('temp',0,8)
 ]) {
  const e=env(data);await render(e.context);
  assert.equal(e.plots.length,0);assert.match(e.status.textContent,/水陆拓扑/);
 }
});
test('line density and opacity change only overlay appearance',()=>{
 const c=env().context,g=c.buildLakeGeometry([0,1,2],[0,1,2],Array.from({length:3},()=>[4,4,4]));
 const all=c.buildLakeGrid(g,{mode:'orthogonal',density:1}),sparse=c.buildLakeGrid(g,{mode:'orthogonal',density:3});
 assert.ok(sparse.x.length<all.x.length);assert.deepEqual(plain(all),plain(c.buildLakeGrid(g,{mode:'orthogonal',density:1,opacity:.1})));
});
test('rendered triangular network has independent edges and nodes above unchanged water faces',async()=>{
 const data={shape:[1,3,3],xc:[0,1,2],yc:[0,1,2],bottom:[[4,4,4],[4,4,4],[4,4,4]],
  water_depth:[[4,4,4],[4,4,4],[4,4,4]],depth:[[[2,2,2],[2,2,2],[2,2,2]]],sigma:[-.5],
  data:[[[1,2,3],[4,5,6],[7,8,9]]],min:1,max:9};
 const render=async mode=>{const e=env(data);await e.context.render3DWaterBody('temp',0,{level:0,meshMode:mode,lineDensity:1,lineOpacity:1,showLand:false,showNetworkNodes:true});return e.plots[0].traces;};
 const triangles=await render('triangles'),orthogonal=await render('orthogonal');
 const triLines=triangles.filter(t=>t.meta?.networkMode==='triangles'&&t.type==='scatter3d'&&t.mode==='lines');
 const triNodes=triangles.find(t=>t.meta?.displayOnly&&t.type==='scatter3d'&&t.mode==='markers');
 const orthoLines=orthogonal.filter(t=>t.meta?.networkMode==='orthogonal'&&t.type==='scatter3d'&&t.mode==='lines');
 assert.ok(triLines.length&&orthoLines.length,'both mesh styles must create visible line overlays');
 const triIndex=triangles.indexOf(triLines[0]),triFaceIndex=triangles.findIndex(t=>t.type==='mesh3d'&&t.intensity);
 assert.ok(triIndex>triFaceIndex,'grid lines must be drawn above the opaque water faces, not hidden behind them');
 assert.ok(triNodes&&triNodes.x.length>0,'triangle network includes visible vertices');
 assert.equal(triLines[0].line.color,'#334a52','triangle edges use a deeper, low-chroma lake slate');
 assert.ok(triLines[0].line.width>=2.25&&triLines[0].line.width<=2.35,'triangle structure remains crisp at a restrained display width');
 assert.notEqual(triLines[0].line.color,'#f1fff8','water network lines must not use near-white highlighting');
 assert.notEqual(triLines[0].line.color,orthoLines[0].line.color,'triangle and orthogonal selections must look different in Plotly, not just carry different metadata');
 assert.ok(triLines.reduce((n,t)=>n+t.x.length,0)>orthoLines.reduce((n,t)=>n+t.x.length,0),
  'triangle mode adds diagonal network edges that orthogonal mode does not draw');
 const faceData=ts=>ts.find(t=>t.type==='mesh3d'&&t.intensity);
 assert.deepEqual(plain([faceData(triangles).i,faceData(triangles).j,faceData(triangles).k]),plain([faceData(orthogonal).i,faceData(orthogonal).j,faceData(orthogonal).k]));
});
test('triangle display keeps source field values and gives internal edges a legible restrained stroke',async()=>{
 const template=fs.readFileSync('3DWET/app/templates/index.html','utf8');
 assert.match(template,/<input id="viz3d-line-opacity"[^>]*value="0\.9"/,
  'the live viewer starts with clearly visible but subdued triangle edges');
 const d={shape:[1,2,2],layer_indices:[0],total_layers:1,xc:[0,1],yc:[0,1],bottom:[[4,4],[4,4]],water_depth:[[4,4],[4,4]],depth:[[[2,2],[2,2]]],sigma:[-.5],
  data:[[[1,2],[3,4]]],min:1,max:4,units:'mg/L'};
 const e=env(d);await e.context.render3DWaterBody('temp',0,{level:0,meshMode:'triangles',showLand:false});
 assert.ok(e.plots[0],e.status.textContent);
 const field=e.plots[0].traces.find(t=>t.meta?.scientificField),edges=e.plots[0].traces.find(t=>t.meta?.networkMode==='triangles'&&t.mode==='lines');
 assert.ok(field&&edges,'triangle mode keeps the existing data trace and derived display-edge trace');
 assert.equal(field.flatshading,true,'triangle faces use subtle flat shading for legible facets');
 assert.deepEqual(plain(field.lighting),{ambient:.48,diffuse:.52,specular:.08,roughness:.82},
  'triangular field facets get a perceptible but restrained display-only directional cue');
 assert.deepEqual(plain(field.lightposition),{x:1000,y:-1200,z:1800},
  'a fixed light direction makes facet relief consistent across updates');
 assert.deepEqual(plain(field.intensity),[1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4],
  'facet vertices retain the source cell values; flat shading does not replace the quantitative field');
 assert.equal(edges.line.color,'#334a52');
 assert.ok(edges.opacity>=.89&&edges.opacity<=.91,'default triangle edges stay visible over field colors without becoming interface-like decoration');
 assert.ok(edges.line.width>=2.25&&edges.line.width<=2.35,'triangle boundaries use a crisp, restrained display-only stroke');
 const ve=e.context.lakeVerticalScale(d.xc,d.yc,d.water_depth);
 assert.ok(Math.abs(edges.meta.displayLift-4*ve*.025)<1e-8,'edge relief is a documented display-only 2.5% of the vertical view span');
 assert.deepEqual(plain(e.plots[0].layout.scene.zaxis.range),[-4*ve,4*ve*.025],'the axis reserves only the required positive display margin');
 assert.match(e.status.textContent,/显示辅助偏移 2\.5%；不代表物理水深\/层位/,'the shifted network is explicitly distinguished from physical depth and layer position');
 assert.ok(!e.plots[0].traces.some(t=>t.meta?.networkMode==='triangles'&&t.mode==='markers'),'triangle nodes are off by default');
});
test('stacked triangular display separates display-only sigma links from surface edges without changing field data',async()=>{
 const d={shape:[2,2,2],layer_indices:[0,1],total_layers:2,xc:[0,1],yc:[0,1],bottom:[[4,4],[4,4]],
  water_depth:[[4,4],[4,4]],depth:[[[3,3],[3,3]],[[1,1],[1,1]]],sigma:[-.75,-.25],
  data:[[[1,2],[3,4]],[[5,6],[7,8]]],min:1,max:8,units:'mg/L'};
 const e=env(d);await e.context.render3DWaterBody('temp',0,{level:1,stack:true,meshMode:'triangles',ve:300,showLand:false});
 const traces=e.plots[0].traces,field=traces.find(t=>t.meta?.scientificField),surface=traces.filter(t=>t.meta?.networkMode==='triangles'&&t.mode==='lines'&&!t.meta?.layerLinks),layers=traces.find(t=>t.meta?.layerLinks);
 assert.deepEqual(plain(field.meta.layerOrdinals),[0,1],'the stacked field trace retains both source layer ordinals');
 assert.equal(surface.length,2,'each physical sigma layer exposes its own display-edge trace');
 assert.ok(layers,'stacked view distinguishes surface triangulation from sigma-column connector lines');
 assert.deepEqual(plain(surface.map(t=>t.meta.layerOrdinal)),[0,1]);
 assert.notEqual(surface[0].line.color,surface[1].line.color,'adjacent strata use distinct muted structure tones');
 assert.equal(layers.meta.displayOnly,true,'sigma-column lines are explicitly a display aid');
 assert.equal(layers.meta.waterbodyFrame,'network');
 assert.equal(layers.line.color,'#657b68','layer links use a restrained secondary structural accent');
 assert.ok(layers.x.length>0&&layers.x.length%3===0,'layer connector trace contains independent line segments');
 assert.equal(layers.meta.displayLift,4*300*.025,'high-VE layer connectors use the documented display-only offset');
 assert.equal(Math.min(...field.intensity),1);assert.equal(Math.max(...field.intensity),8);
 assert.equal(field.intensity.length,32,'display lighting and connector lines preserve every stacked source field vertex');
 const orthogonal=env(d);await orthogonal.context.render3DWaterBody('temp',0,{level:1,stack:true,meshMode:'orthogonal',ve:300,showLand:false});
 const orthogonalField=orthogonal.plots[0].traces.find(t=>t.meta?.scientificField);
 assert.deepEqual(plain(field.intensity),plain(orthogonalField.intensity),'display structure leaves quantitative field values unchanged');
 assert.deepEqual(plain([field.i,field.j,field.k]),plain([orthogonalField.i,orthogonalField.j,orthogonalField.k]),
  'separate display connectors do not alter field surface topology');
 assert.match(e.status.textContent,/层间连接线仅为显示辅助/,'the added layer cue is labeled as non-physical display structure');
});
test('stacked triangular display adds shaded inter-layer side facets without changing science or bed geometry',async()=>{
 const d={shape:[2,2,2],layer_indices:[0,1],total_layers:2,xc:[0,1],yc:[0,1],bottom:[[4,4],[4,4]],
  water_depth:[[4,4],[4,4]],depth:[[[3,3],[3,3]],[[1,1],[1,1]]],sigma:[-.75,-.25],
  data:[[[1,2],[3,4]],[[5,6],[7,8]]],min:1,max:8,units:'mg/L'};
 const e=env(d);await e.context.render3DWaterBody('temp',0,{level:1,stack:true,meshMode:'triangles',ve:1,showLand:false,showBedSurface:true});
 const traces=e.plots[0].traces,field=traces.find(t=>t.meta?.scientificField),bed=traces.find(t=>t.meta?.waterbodyFrame==='bed');
 const facets=traces.find(t=>t.meta?.layerStructureFacets===true);
 assert.ok(facets,'a multi-layer triangle view renders actual side facets between consecutive wet layers');
 assert.equal(facets.type,'mesh3d');assert.equal(facets.meta.displayOnly,true);
 assert.equal(facets.showscale,false);assert.equal(facets.cmin,undefined);assert.equal(facets.intensity,undefined,
  'structural facets have no quantitative color mapping or copied field values');
 assert.equal(facets.opacity,.22,'the neutral layer sides reveal structure without masking the data surfaces');
 assert.equal(facets.flatshading,true,'side facets carry directional depth cues');
 assert.ok(facets.i.length>0&&facets.i.length%2===0,'each inter-layer quadrilateral is rendered as two stable triangles');
 assert.deepEqual(plain(field.meta.layerOrdinals),[0,1]);
 assert.deepEqual(plain(field.intensity),[1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,6,6,6,6,7,7,7,7,8,8,8,8],
  'the original field samples remain byte-for-byte represented on both strata');
 assert.equal(field.cmin,1);assert.equal(field.cmax,8);
 assert.equal(facets.colorscale,undefined);assert.equal(facets.cmin,undefined);assert.equal(facets.cmax,undefined);
 const geometry=e.context.buildLakeGeometry(d.xc,d.yc,d.water_depth,1);
 const sparseLayers=e.context.lakePhysicalVolumeNetwork({...d,layer_indices:[0,2]},geometry,1);
 assert.equal(e.context.lakeInterlayerSideFacetMesh(sparseLayers,1,[0,2]).i.length,0,
  'a gap in original layer ordinals is not disguised as a physically adjacent stratum');
 assert.deepEqual(plain(bed.z),plain(env(d).context.buildLakeGeometry(d.xc,d.yc,d.bottom,1).floor.z),
  'adding layer structure does not move or rebuild the real bathymetric surface');
 assert.ok(new Set(facets.z).size>1,'side facets span the actual neighboring sigma-layer elevations');
 assert.match(e.status.textContent,/侧面为显示辅助/,'the interpolated panels are disclosed as display geometry');
});
test('triangle network alternates diagonal edge orientation into a visible wireframe',()=>{
 const c=env().context,g=c.buildLakeGeometry([0,1,2,3],[0,1,2],Array.from({length:3},()=>[4,4,4,4]));
 const line=c.buildLakeGrid(g,{mode:'triangles',density:1});
 const diagonalSlopes=new Set();
 for(let q=0;q<line.x.length;q+=3){
  if(line.x[q]===null||line.x[q+1]===null)continue;
  if(line.x[q]!==line.x[q+1]&&line.y[q]!==line.y[q+1])
   diagonalSlopes.add(Math.sign((line.x[q+1]-line.x[q])*(line.y[q+1]-line.y[q])));
 }
 assert.ok(diagonalSlopes.has(1)&&diagonalSlopes.has(-1),
  'neighboring wet cells must use opposite diagonals, exposing a triangular wireframe');
});
test('triangular volume network adds diagonals across sigma-column side quads',()=>{
 const c=env().context,plane=z=>({x:[0,1,1,0],y:[0,0,1,1],z:[z,z,z,z],cell:[[0,0],[0,0],[0,0],[0,0]]});
 const network=c.buildDisplayNetwork([plane(0),plane(1)],{mode:'triangles',density:1,refinement:1});
 const sideDiagonals=[];
 for(let q=0;q+1<network.lines.x.length;q+=3){
  const a=[network.lines.x[q],network.lines.y[q],network.lines.z[q]],b=[network.lines.x[q+1],network.lines.y[q+1],network.lines.z[q+1]];
  if(Number.isFinite(a[0])&&Number.isFinite(b[0])&&a[2]!==b[2]&&(a[0]!==b[0]||a[1]!==b[1]))sideDiagonals.push([a,b]);
 }
 assert.equal(sideDiagonals.length,5,'each of the four cell edges and its face diagonal get one cross-layer side diagonal');
});
test('triangle subdivision templates are reused by refinement while network heights remain per-frame',()=>{
 const c=env().context;
 const template=c.lakeTriangleNetworkTemplate(3);
 assert.ok(template,'triangle refinement must have a cached, geometry-independent template');
 assert.equal(c.lakeTriangleNetworkTemplate(3),template,'same refinement should reuse its immutable index/weight template');
 assert.notEqual(c.lakeTriangleNetworkTemplate(4),template,'a different refinement must use its own subdivision topology');
 const plane=(base)=>({x:[0,1,1,0],y:[0,0,1,1],z:[base,base,base,base],cell:[[0,0],[0,0],[0,0],[0,0]]});
 const lower=plane(-1),upper=plane(-2),opts={mode:'triangles',density:1,refinement:3};
 const first=c.buildDisplayNetwork([lower,upper],opts).lines;
 lower.z.fill(-3);upper.z.fill(-5);
 const next=c.buildDisplayNetwork([lower,upper],opts).lines;
 assert.notDeepEqual(plain(next.z),plain(first.z),'cached topology must evaluate current-frame layer heights on every render');
 assert.deepEqual(plain(next.x),plain(first.x));assert.deepEqual(plain(next.y),plain(first.y));
});
test('dynamic triangular display lines follow current wet cells while missing and dry cells stay distinct',async()=>{
 const payloadAt=frame=>({shape:[1,2,3],xc:[0,1,2],yc:[0,1],bottom:[[5,5,0],[5,5,5]],
  water_depth:[[5+frame,5+frame,null],[5+frame,5+frame,5+frame]],depth:[[[2+frame,3+frame,null],[4+frame,5+frame,6+frame]]],sigma:[-.5],
  valid_geometry:[[true,true,false],[true,true,true]],dry_mask:[[false,false,true],[false,false,false]],
  data:[[[1,null,null],[3,4,5]]],min:1,max:5,long_name:'fixture'});
 const c=env(payloadAt(0)).context,first=fixtureTopology(payloadAt(0)),geometry=c.buildLakeGeometry(first.xc,first.yc,first.bottom,1);
 const corner=c.lakeLayerCornerAverages(geometry,first,0,false),fields=c.lakeLayerMeshes(geometry,first,0,1,false,corner);
 assert.deepEqual(plain(fields.fieldMesh.cell.filter((_cell,index)=>index%4===0)),[[0,0],[0,1],[1,1],[2,1]],'each finite confirmed wet cell receives a display face, with dry cells absent');
 assert.deepEqual(plain(fields.missingMesh.cell.filter((_cell,index)=>index%4===0)),[[1,0]],'the wet missing-value cell remains represented only by missing material');
 const mesh0=c.lakePhysicalVolumeNetwork(first,geometry,1),network0=c.lakeDisplayLines(mesh0,geometry,{meshMode:'triangles'},first)[0];
 assert.equal(new Set(mesh0[0].cell.filter((_cell,index)=>index%4===0).map(cell=>JSON.stringify(cell))).size,5,'wire network includes each valid wet structure cell, including the cell with missing scalar data');
 assert.ok(network0.meta.displayOnly&&network0.meta.networkMode==='triangles','triangles are a display overlay generated from the active wet structure');
 const nextData=fixtureTopology(payloadAt(1)),mesh1=c.lakePhysicalVolumeNetwork(nextData,geometry,1),network1=c.lakeDisplayLines(mesh1,geometry,{meshMode:'triangles'},nextData)[0];
 assert.deepEqual(plain(network1.x),plain(network0.x),'frame advancement preserves active wet topology in the wire overlay');
 assert.deepEqual(plain(network1.y),plain(network0.y));
 assert.notDeepEqual(plain(network1.z),plain(network0.z),'frame advancement updates dynamic triangle line elevations');
});
test('land plane uses only explicitly dry cells, including island holes; unknown bathymetry stays absent',()=>{
 const c=env().context,land=c.buildLakeLand({xc:[0,1,2],yc:[0,1],dry_mask:[[true,false,false],[false,true,false]],bottom:[[null,4,null],[3,null,null]]});
 assert.equal(land.i.length,4);assert.ok(land.z.every(v=>v===0));assert.deepEqual(plain(land.cell),[[0,0],[0,0],[0,0],[0,0],[1,1],[1,1],[1,1],[1,1]]);
 assert.equal(c.buildLakeLand({xc:[0],yc:[0],bottom:[[null]]}).i.length,0);
});
const payload={shape:[1,2,2],xc:[0,1],yc:[0,1],bottom:[[4,4],[4,null]],water_depth:[[4,4],[4,null]],
 dry_mask:[[false,false],[false,true]],valid_geometry:[[true,true],[false,false]],depth:[[[2,2],[null,null]]],sigma:[-.5],
 data:[[[1,null],[7,null]]],min:1,max:1,units:'mg/L'};
test('missing wet scalar has separate material and never fills invalid geometry or numeric scale',async()=>{
 const e=env(payload);await e.context.render3DWaterBody('x',0,{level:0,meshMode:'triangles'});
 const traces=e.plots[0].traces,missing=traces.find(t=>t.meta?.missingWater),field=traces.find(t=>t.intensity?.includes(1)&&t.name?.includes('层'));
 assert.ok(missing);assert.equal(missing.i.length,2);assert.equal(missing.showscale,false);assert.equal(missing.intensity,undefined);
 assert.ok(field);assert.deepEqual([...new Set(field.intensity)],[1]);assert.equal(field.i.length,2);
 assert.match(e.status.textContent,/缺测/);assert.match(e.status.textContent,/陆地高程未提供/);
});
test('all missing scalar still shows physically located missing material without numeric colorbar',async()=>{
 const d={...payload,data:[[[null,null],[null,null]]],min:null,max:null},e=env(d);
 await e.context.render3DWaterBody('x',0,{level:0});assert.equal(e.plots.length,1);
 assert.ok(e.plots[0].traces.some(t=>t.meta?.missingWater));assert.ok(e.plots[0].traces.every(t=>!t.showscale));
});
test('display controls are explicitly display-only and call the existing renderer',()=>{
 const html=fs.readFileSync('3DWET/app/templates/index.html','utf8'),app=fs.readFileSync('3DWET/app/static/js/app.js','utf8');
 assert.match(html,/\/static\/js\/viz3d\.js\?v=\d+/,'desktop page must include a versioned renderer URL so cached scripts can be invalidated');
 for(const id of ['viz3d-mesh-mode','viz3d-line-density','viz3d-line-opacity','viz3d-show-land','viz3d-mesh-nodes']){assert.ok(html.includes(`id="${id}"`));assert.ok(app.includes(`$('${id}')`));}
 for(const value of ['continuous','orthogonal','triangles','hidden'])assert.ok(html.includes(`value="${value}"`));
 assert.match(html,/仅改变显示/);assert.match(html,/陆地高程未提供/);
});
test('first 3D view defaults to continuous display while retaining alternatives',()=>{
 const html=fs.readFileSync('3DWET/app/templates/index.html','utf8');
 const select=html.match(/<select class="form-select" id="viz3d-mesh-mode"[^>]*>([\s\S]*?)<\/select>/)?.[1];
 assert.ok(select,'3D mesh selector must exist');
 assert.match(select,/<option value="continuous" selected>/,'first open uses the continuous surface display');
 for(const value of ['orthogonal','triangles','hidden'])assert.match(select,new RegExp(`<option value="${value}"(?: selected)?>`));
});
test('high-quality 3D water rendering can resolve Dianchi shoreline at native mesh resolution',()=>{
 const html=fs.readFileSync('3DWET/app/templates/index.html','utf8'),app=fs.readFileSync('3DWET/app/static/js/app.js','utf8');
 const quality=html.match(/<select class="form-select" id="viz3d-iso-quality"[^>]*>([\s\S]*?)<\/select>/)?.[1]||'';
 assert.match(quality,/<option value="64"[^>]*>中等/,'medium resolution should substantially reduce mixed shoreline blocks');
 assert.match(quality,/<option value="96" selected[^>]*>高/,'the default high resolution must retain native shoreline cells for the 82×41 Dianchi grid');
 assert.match(app,/Number\(\$\('viz3d-iso-quality'\)\?\.value \|\| 96\)/,'fallback quality should match the selected high-resolution preset');
});
test('cloud includes missing native positions in the selected missing colour, without numeric legend values',async()=>{
 const e=env(payload);await e.context.render3DCloud('x',0,26,{});
 const missing=e.plots[0].traces.find(t=>t.meta?.missingWater);assert.ok(missing);
 assert.deepEqual(plain(missing.x),[1]);assert.deepEqual(plain(missing.z),[-2]);assert.equal(missing.marker.showscale,false);
 assert.ok(e.plots[0].traces.some(t=>t.meta?.landPlane));assert.match(e.status.textContent,/几何缺失 1/);
});
test('all-missing cloud has physically located markers and explicit coverage rather than claiming land',async()=>{
 const e=env({...payload,data:[[[null,null],[null,null]]],min:null,max:null});await e.context.render3DCloud('x',0,26,{});
 assert.equal(e.plots.length,1);assert.match(e.status.textContent,/水域缺测 2/);assert.ok(e.plots[0].traces.every(t=>!t.marker?.showscale));
});
test('variable-height wet-cell faces cannot bridge an island or missing scalar height',()=>{
 const c=env().context,g={xc:[0,1,2],yc:[0,1,2],wetMask:[[true,true,true],[true,false,true],[true,true,true]],dry_mask:[[false,false,false],[false,true,false],[false,false,false]]};
 const values=[[1,2,3],[4,1234,null],[5,6,7]],before=plain(values),mesh=c.buildVariableHeightMesh(values,g);
 assert.equal(mesh.i.length,14);assert.ok(mesh.z.every(Number.isFinite));assert.ok(!mesh.z.includes(1234));
 assert.deepEqual(plain(values),before);for(let q=0;q<mesh.z.length;q++)assert.equal(mesh.z[q],values[mesh.cell[q][1]][mesh.cell[q][0]]);
});

test('variable-height triangle network changes display traces without changing mesh faces or bridging dry cells',()=>{
 const c=env().context,grid={xc:[0,1,2],yc:[0,1],wetMask:[[true,true,true],[true,false,true]]};
 const values=[[1,2,3],[4,null,6]],before=plain(values);
 const orthogonal=c.buildVariableHeightMesh(values,grid,'orthogonal');
 const triangles=c.buildVariableHeightMesh(values,grid,'triangles');
 function diagonal(mesh,cell){
  const vertices=[];mesh.cell.forEach((value,index)=>{if(value[0]===cell[0]&&value[1]===cell[1])vertices.push(index);});
  assert.equal(vertices.length,4);
  const local=new Map(vertices.map((index,q)=>[index,q])),faces=[];
  for(let q=0;q<mesh.i.length;q++){
   const face=[mesh.i[q],mesh.j[q],mesh.k[q]];
   if(face.every(index=>local.has(index)))faces.push(new Set(face.map(index=>local.get(index))));
  }
  assert.equal(faces.length,2);
  return [...faces[0]].filter(index=>faces[1].has(index)).sort((a,b)=>a-b);
 }
 assert.deepEqual(diagonal(orthogonal,[0,0]),[0,2]);
 assert.deepEqual(diagonal(orthogonal,[1,0]),[0,2]);
 assert.deepEqual(diagonal(triangles,[0,0]),diagonal(orthogonal,[0,0]));
 assert.deepEqual(diagonal(triangles,[1,0]),diagonal(orthogonal,[1,0]));
 assert.deepEqual(plain(triangles.cell.filter(cell=>cell[0]===1&&cell[1]===1)),[],'dry grid cells cannot gain variable-height faces');
 assert.deepEqual(plain(values),before,'network overlay leaves scalar values unchanged');
 const network=c.buildLakeGrid({floor:triangles,nx:3,ny:2},{mode:'triangles'});
 const baseNetwork=c.buildLakeGrid({floor:triangles,nx:3,ny:2},{mode:'orthogonal'});
 assert.ok(network.x.length>baseNetwork.x.length,'triangle network adds independent internal diagonals');
});

test('different scalar heights retain both distinct grid edges at the shared horizontal position',()=>{
 const c=env().context,mesh=c.buildVariableHeightMesh([[1,2]],{xc:[0,1],yc:[0],wetMask:[[true,true]]});
 const lines=c.buildLakeGrid({floor:mesh,nx:2,ny:1},{mode:'orthogonal',density:1}),heights=[];
 for(let q=0;q<lines.x.length;q+=3)if(lines.x[q]===.5&&lines.x[q+1]===.5)heights.push(lines.z[q]);
 assert.deepEqual(heights.sort((a,b)=>a-b),[1,2]);
});
test('depth axes have compact titles with complete exported datum annotations',async()=>{
 const e=env({...payload,depth_reference:'below native 3D geometry surface'});await e.context.render3DWaterBody('x',0,{level:0});
 assert.ok(e.plots[0].layout.scene.zaxis.title.length<22);assert.match(e.plots[0].layout.title.text,/三维水面为0/);
});

test('desktop plot title keeps two concise lines while full display evidence remains in status',async()=>{
 const topology={contract:'sampled-wet-topology-v1',source_shape:[200,300],x_indices:[0,150],y_indices:[0,100],
  sampling_stride:[100,150],grid_hash:'sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',mask_cells_examined:60000,
  x_edges:[-.5,149.5,299.5],y_edges:[-.5,99.5,199.5],cell_status:[['wet','wet'],['wet','dry']],
  wet_mask:[[true,true],[true,false]],land_mask:[[false,false],[false,true]],wall_sides:[[[false,false,false,false],[false,false,false,false]],[[false,false,false,false],[false,false,false,false]]],mixed_or_unknown_cells:0};
 const e=env({...payload,depth_reference:'below native 3D geometry surface',full_shape:[1,200,300],sampling_stride:[1,10,15],
  x:[0,150],y:[0,100],display_topology:topology});
 await e.context.render3DWaterBody('x',0,{level:0,timeLabel:'2026-DOY290 12:30:00'});
 const title=e.plots[0].layout.title.text;
 assert.ok(title.split('<br>').length<=2,title);
 assert.match(title.split('<br>')[0],/三维水面为0/);
 assert.match(title,/2026-DOY290 12:30:00/);assert.match(title,/层 0\/0/);assert.match(title,/采样/);
 assert.doesNotMatch(title,/陆地高程未提供|求解器拓扑|悬停|几何缺失/);
 for(const term of ['陆地高程未提供','求解器拓扑','几何缺失','200×300'])assert.ok(e.status.textContent.includes(term));
});
test('continuous scalar interpolation is display-only, preserves native centre hover, and isolates diagonal cells',()=>{
 const c=env().context,d={shape:[1,2,2],xc:[0,1],yc:[0,1],bottom:[[2,8],[0,0]],sigma:[-.5],data:[[[0,10],[null,null]]]};
 const g=c.buildLakeGeometry(d.xc,d.yc,d.bottom),before=plain(d),smoothCorners=c.lakeLayerCornerAverages(g,d,0,true),nativeCorners=c.lakeLayerCornerAverages(g,d,0,false);
 const smooth=c.lakeLayerMeshes(g,d,0,1,true,smoothCorners).fieldMesh,native=c.lakeLayerMeshes(g,d,0,1,false,nativeCorners).fieldMesh;
 assert.ok(smooth.intensity.includes(5));assert.deepEqual(plain(native.intensity),[0,0,0,0,10,10,10,10]);
 assert.equal(smooth.customdata[1][6],0);assert.deepEqual(plain(d),before);
 const diagonal={...d,bottom:[[2,0],[0,8]],data:[[[0,null],[null,10]]]};
 const dg=c.buildLakeGeometry(d.xc,d.yc,diagonal.bottom),dc=c.lakeLayerCornerAverages(dg,diagonal,0,true),dm=c.lakeLayerMeshes(dg,diagonal,0,1,true,dc).fieldMesh;
 assert.deepEqual(plain(dm.intensity),[0,0,0,0,10,10,10,10]);assert.deepEqual(plain(dg.floor.z),[-2,-2,-2,-2,-8,-8,-8,-8]);
});

test('compact singleton top-layer sigma uses authoritative center depth instead of bed fallback',()=>{
 const c=env().context,d={shape:[1,1,2],xc:[0,1],yc:[0],bottom:[[0.68940,15.26806]],
  depth:[[[0.03448,0.76337]]],sigma:[0],data:[[[0.46,0.497]]]};
 const geometry=c.buildLakeGeometry(d.xc,d.yc,d.bottom,300),corners=c.lakeLayerCornerAverages(geometry,d,0,false);
 const field=c.lakeLayerMeshes(geometry,d,0,300,false,corners).fieldMesh;
 assert.ok(field.z.every((z,index)=>Math.abs(z-geometry.floor.z[index])>1e-6),
  'each scientific layer vertex must remain distinct from its corresponding bed vertex');
 assert.ok(Math.max(...field.z.map(Math.abs))<Math.max(...geometry.floor.z.map(Math.abs))/10,
  'surface-center depth must remain near the surface, not the bed');
});

test('lake layer faces stay fixed while wet-cell network mode controls only visible overlays',()=>{
 const c=env().context,bottom=[[4,4,4],[4,0,4]],d={
  shape:[1,2,3],xc:[0,1,2],yc:[0,1],bottom,depth:[[[2,2,2],[2,null,2]]],sigma:[-.5],
  valid_geometry:[[true,true,true],[true,false,true]],
  data:[[[1,2,3],[4,null,6]]],elevation:[[[10,20,30],[40,null,60]]]
 };
 const geometry=c.buildLakeGeometry(d.xc,d.yc,bottom),before=plain(d);
 function cellDiagonal(mesh,cell){
  const vertices=[];
  mesh.cell.forEach((value,index)=>{if(value[0]===cell[0]&&value[1]===cell[1])vertices.push(index);});
  assert.equal(vertices.length,4,`expected a single four-corner face for wet cell ${cell}`);
  const local=new Map(vertices.map((index,q)=>[index,q])),triangles=[];
  for(let q=0;q<mesh.i.length;q++){
   const face=[mesh.i[q],mesh.j[q],mesh.k[q]];
   if(face.every(index=>local.has(index)))triangles.push(new Set(face.map(index=>local.get(index))));
  }
  assert.equal(triangles.length,2,`wet cell ${cell} must remain two real face triangles`);
  const diagonal=[...triangles[0]].filter(index=>triangles[1].has(index)).sort((a,b)=>a-b);
  assert.equal(diagonal.length,2,'two face triangles must share exactly one cell diagonal');
  return diagonal;
 }
 const cornerAverages=c.lakeLayerCornerAverages(geometry,d,0,false);
 const orthogonal=c.lakeLayerMeshes(geometry,d,0,1,false,cornerAverages).fieldMesh;
 const triangles=c.lakeLayerMeshes(geometry,d,0,1,false,cornerAverages).fieldMesh;
 assert.deepEqual(cellDiagonal(orthogonal,[0,0]),[0,2]);
 assert.deepEqual(cellDiagonal(orthogonal,[1,0]),[0,2]);
 assert.deepEqual(cellDiagonal(triangles,[0,0]),[0,2]);
 assert.deepEqual(cellDiagonal(triangles,[1,0]),cellDiagonal(orthogonal,[1,0]),
  'network mode cannot alter colored surface faces');
 assert.equal(cellDiagonal(triangles,[0,1]).length,2,'isolated wet cell next to a dry cell remains represented');
 assert.deepEqual(plain(d),before,'display tessellation cannot mutate native fields, geometry, or hover payloads');
 for(const index of triangles.i.concat(triangles.j,triangles.k))assert.notDeepEqual(plain(triangles.cell[index]),[1,1],
  'dry cell faces must never be generated');
 const missingData={...d,data:[[[1,null,3],[4,null,6]]]};
 const missingCorners=c.lakeLayerCornerAverages(geometry,missingData,0,false);
 const missing=c.lakeLayerMeshes(geometry,missingData,0,1,false,missingCorners).missingMesh;
 assert.deepEqual(cellDiagonal(missing,[1,0]),cellDiagonal(orthogonal,[1,0]),
  'missing-value display faces stay independent of network style and have no scalar intensity');
 assert.equal(missing.intensity,undefined);
});

test('triangular network is rendered as wet-cell node and edge traces with inter-layer links, independent of surface faces',async()=>{
 const d={shape:[2,2,3],xc:[0,1,2],yc:[0,1],bottom:[[4,4,4],[4,0,4]],
  depth:[[[1,1,1],[1,null,1]],[[3,3,3],[3,null,3]]],sigma:[-.75,-.25],
  valid_geometry:[[true,true,true],[true,false,true]],data:[[[1,2,3],[4,null,6]],[[7,8,9],[10,null,12]]],min:1,max:12};
 const render=async mode=>{const e=env(d);await e.context.render3DWaterBody('temp',0,{level:1,stack:true,meshMode:mode,lineDensity:1,lineOpacity:1,showLand:false,showNetworkNodes:true});return e.plots[0].traces;};
 const triangle=await render('triangles'),orthogonal=await render('orthogonal');
 const triLines=triangle.find(t=>t.meta?.networkMode==='triangles'&&t.type==='scatter3d'&&t.mode==='lines');
 const triNodes=triangle.find(t=>t.meta?.displayOnly&&t.type==='scatter3d'&&t.mode==='markers');
 const orthoLines=orthogonal.find(t=>t.meta?.networkMode==='orthogonal'&&t.type==='scatter3d'&&t.mode==='lines');
 assert.ok(triLines&&triNodes,'triangle network must draw separate connected edges and visible nodes');
 assert.equal(triLines.meta.networkMode,'triangles');assert.equal(triNodes.meta.networkMode,'triangles');
 assert.ok(triLines.x.filter(Number.isFinite).length/3>orthoLines.x.filter(Number.isFinite).length/3,'triangular network includes diagonals');
 const faceTraces=traces=>traces.filter(t=>t.type==='mesh3d'&&t.intensity);
 assert.deepEqual(plain(faceTraces(triangle).map(t=>[t.i,t.j,t.k])),plain(faceTraces(orthogonal).map(t=>[t.i,t.j,t.k])),
  'mesh selection affects visible networks only, never colored surface face topology');
 assert.ok(triNodes.x.every((x,q)=>Number.isFinite(x)&&Number.isFinite(triNodes.y[q])&&Number.isFinite(triNodes.z[q])));
 const networkLines=[triLines,...triangle.filter(t=>t.meta?.layerLinks)];
 const segmentKeys=new Set();for(const trace of networkLines)for(let q=0;q<trace.x.length;q+=3)if(Number.isFinite(trace.x[q])&&Number.isFinite(trace.x[q+1]))segmentKeys.add([[trace.x[q],trace.y[q],trace.z[q]],[trace.x[q+1],trace.y[q+1],trace.z[q+1]]].map(p=>p.join(',')).sort().join('|'));
 const layers=[...new Set(triNodes.z)].sort((a,b)=>a-b),vertical=[];
 for(const key of segmentKeys){const [a,b]=key.split('|').map(p=>p.split(',').map(Number));if(a[0]===b[0]&&a[1]===b[1]&&a[2]!==b[2])vertical.push([a,b]);}
 assert.ok(vertical.length>0,'volume network must connect corresponding wet-cell vertices between sigma layers');
 for(const trace of networkLines)for(let q=0;q+1<trace.x.length;q+=3)if(Number.isFinite(trace.x[q])&&Number.isFinite(trace.x[q+1])){
  const mx=(trace.x[q]+trace.x[q+1])/2,my=(trace.y[q]+trace.y[q+1])/2;
  assert.ok(!(mx>.5&&mx<1.5&&my>.5&&my<1.5),'no network edge may cross the interior of the dry native cell');
 }
});

test('triangle wire nodes are optional and hidden by default for a clean reference-style surface',async()=>{
 const e=env(payload);await e.context.render3DWaterBody('temp',0,{level:0,meshMode:'triangles',showLand:false});
 assert.ok(e.plots[0].traces.some(t=>t.meta?.networkMode==='triangles'&&t.mode==='lines'));
 assert.ok(!e.plots[0].traces.some(t=>t.meta?.displayOnly&&t.mode==='markers'));
 const withNodes=env(payload);await withNodes.context.render3DWaterBody('temp',0,{level:0,meshMode:'triangles',showNetworkNodes:true,showLand:false});
 assert.ok(withNodes.plots[0].traces.some(t=>t.meta?.displayOnly&&t.mode==='markers'));
});

test('3D triangle lines are labeled as a display triangulation, not native solver topology',()=>{
 const html=fs.readFileSync('3DWET/app/templates/index.html','utf8');
 assert.match(html,/option value="orthogonal">正交网格线/);
 assert.match(html,/option value="triangles">三角网格（显示剖分）/);
 assert.match(html,/拖动旋转，滚轮缩放/,'the camera interaction is discoverable beside the view controls');
 assert.match(html,/本案例为结构四边形网格/);
 assert.match(html,/图例随当前帧列出实际参与绘制的湿单元与显示边/);
 assert.match(html,/不是求解器原生三角拓扑/);
 assert.match(html,/默认以稳定对角线将当前有效湿四边形显示为三角面/);
 assert.match(html,/网格线间距/);
 assert.match(html,/网格线透明度/);
});

for(const renderer of ['render3DSurface'])test(`${renderer} keeps missing material and known land even without a drawable contour`,async()=>{
 const e=env({...payload,data:[[[null,null],[null,null]]],min:null,max:null});await e.context[renderer]('x',0,26,{});
 assert.equal(e.plots.length,1);assert.ok(e.plots[0].traces.some(t=>t.meta?.missingWater));
 assert.ok(e.plots[0].traces.some(t=>t.meta?.landPlane));assert.ok(e.plots[0].traces.every(t=>!t.showscale&&!t.marker?.showscale));
 assert.match(e.status.textContent,/水域缺测 2/);assert.match(e.status.textContent,/等值面/);
});
test('variable-height renderer uses validated scientific-grid wet cells, actual coordinates, and neutral land reference',async()=>{
 const d={data:[[0,null],[99,-2]],min:-2,max:0,units:'mg/L'},g={shape:[2,2],xc:[100,200],yc:[300,500],coordinate_mode:'projected',coordinate_units:'m',wetMask:[[true,true],[false,true]],dry_mask:[[false,false],[true,false]]};
 const e=env(d,g);await e.context.render2DAs3DSurface('x',0,0,{meshMode:'triangles',showNetworkNodes:true});
 assert.equal(e.plots.length,1);const p=e.plots[0],field=p.traces.find(t=>t.meta?.variableHeight);
 assert.equal(field.i.length,4);assert.deepEqual(plain(field.z),[0,0,0,0,-2,-2,-2,-2]);assert.ok(!field.z.includes(99));
 assert.deepEqual(plain(p.layout.scene.xaxis.range),[50,250]);assert.deepEqual(plain(p.layout.scene.yaxis.range),[200,600]);
 assert.ok(p.traces.some(t=>t.meta?.landPlane));assert.match(p.layout.scene.zaxis.title,/mg\/L/);assert.doesNotMatch(p.layout.scene.zaxis.title,/水深/);
 assert.ok(p.traces.some(t=>t.meta?.networkMode==='triangles'&&t.mode==='lines')&&p.traces.some(t=>t.meta?.networkMode==='triangles'&&t.mode==='markers'),
  'variable-height 2D-as-3D also draws the independent triangular node and edge network');
 const orth=env(d,g);await orth.context.render2DAs3DSurface('x',0,0,{meshMode:'orthogonal'});
 const orthField=orth.plots[0].traces.find(t=>t.meta?.variableHeight);
 assert.deepEqual(plain([field.i,field.j,field.k]),plain([orthField.i,orthField.j,orthField.k]),'variable-height colored faces are independent of network choice');
 assert.match(e.status.textContent,/变量值|变量原值/);assert.match(e.status.textContent,/缺测.*高度/);
 const bad=env(d,{...g,shape:[2,3]});await bad.context.render2DAs3DSurface('x',0,0,{});assert.equal(bad.plots.length,0);assert.match(bad.status.textContent,/网格|geometry|匹配/);
});

test('rendered mesh modes change only display geometry and preserve exact native hover values',async()=>{
 const e=env(payload),before=plain(payload),fields=[];
 for(const meshMode of ['continuous','orthogonal','triangles','hidden']){
  await e.context.render3DWaterBody('x',0,{level:0,meshMode,lineDensity:1,lineOpacity:.17,showLand:false});
  const plot=e.plots.at(-1),field=plot.traces.find(t=>t.intensity?.includes(1)&&t.name?.includes('层'));
  fields.push(field);const lines=plot.traces.filter(t=>['orthogonal','triangles'].includes(t.meta?.networkMode)&&t.mode==='lines');
  assert.equal(lines.length>0,['orthogonal','triangles'].includes(meshMode));for(const line of lines)assert.equal(line.opacity,.17);
  assert.ok(!plot.traces.some(t=>t.meta?.landPlane));
 }
 for(const field of fields){assert.deepEqual(plain(field.z),plain(fields[0].z));assert.deepEqual(plain(field.customdata),plain(fields[0].customdata));}
 assert.deepEqual(plain(payload),before);
});

test('fine triangular wire refinement subdivides only the existing wet-cell triangles without changing their source mesh',()=>{
 const c=env().context,grid={xc:[0,1,2],yc:[0,1],wetMask:[[true,true,true],[true,false,true]]};
 const values=[[0,10,20],[30,null,50]],mesh=c.buildVariableHeightMesh(values,grid);
 const before=plain(mesh),coarse=c.buildLakeGrid({floor:mesh,nx:3,ny:2},{mode:'triangles',density:1,refinement:1});
 const fine=c.buildLakeGrid({floor:mesh,nx:3,ny:2},{mode:'triangles',density:1,refinement:4});
 assert.ok(fine.x.filter(Number.isFinite).length>coarse.x.filter(Number.isFinite).length*3,
  'triangle refinement must visibly subdivide each wet-cell triangle, not only draw one coarse diagonal');
 assert.deepEqual(plain(mesh),before,'display refinement cannot alter solver faces, values, or hover data');
 for(let q=0;q+1<fine.x.length;q+=3){
  if(!Number.isFinite(fine.x[q])||!Number.isFinite(fine.x[q+1]))continue;
  const midpoint=[(fine.x[q]+fine.x[q+1])/2,(fine.y[q]+fine.y[q+1])/2];
  assert.ok(!(midpoint[0]>.5&&midpoint[0]<1.5&&midpoint[1]>.5&&midpoint[1]<1.5),
   'subdivided network must not enter a dry cell');
 }
});

test('static reference lake view uses the wet boundary without square dry-cell land tiling',async()=>{
 const d={...payload,shape:[1,2,3],xc:[0,1,2],yc:[0,1],bottom:[[4,4,0],[4,0,0]],water_depth:[[4,4,0],[4,0,0]],
  dry_mask:[[false,false,true],[false,true,true]],valid_geometry:[[true,true,false],[true,false,false]],
  depth:[[[2,3,null],[4,null,null]]],data:[[[1,2,null],[3,null,null]]],min:1,max:3};
 const e=env(d);await e.context.render3DWaterBody('temp',0,{level:0,overlay:false,meshMode:'triangles',showBedSurface:true});
 assert.ok(!e.plots[0].traces.some(t=>t.meta?.landNetwork||t.meta?.landPlane),
  'static depth previews omit tiled dry-cell land when land elevation is unavailable');
 assert.ok(e.plots[0].traces.some(t=>t.meta?.shoreline),'the generalized wet boundary remains visible');
 assert.ok(e.plots[0].traces.some(t=>t.meta?.coastalRim),'verified wet-to-land edges retain the coastal depth transition');
 const scale=e.plots[0].traces.find(t=>t.name==='湖盆水深').colorscale;
 assert.ok(scale.some(([t,c])=>t===0&&c==='#75e3d7'));
 assert.ok(scale.some(([t,c])=>t===1&&c==='#173fbd'));
});

test('high-VE overlay bed scale stays in depth units while the field keeps its selected-variable range',async()=>{
 const d={shape:[1,2,2],xc:[0,100],yc:[0,100],
  bottom:[[2,4],[6,8]],water_depth:[[2,4],[6,8]],depth:[[[1,2],[3,4]]],sigma:[-.5],
  data:[[[10,15],[20,25]]],min:10,max:25,units:'mg/L'};
 const e=env(d),geometry=e.context.buildLakeGeometry(d.xc,d.yc,d.water_depth,100);
 const style={min:10,max:25,colorscale:[[0,'#112233'],[1,'#ddeeff']]};
 const traces=e.context.lakeTraces(geometry,false,d,style,{dynamicOverlay:true,showBedSurface:true});
 const bed=traces.find(trace=>trace.meta?.waterbodyFrame==='bed');
 assert.ok(Array.isArray(bed.colorscale),'high-VE dynamic bed keeps its depth palette');
 assert.equal(bed.color,undefined,'bed color must come from vertex intensity and the depth colorscale');
 assert.equal(bed.intensitymode,'vertex','bed depth colors are interpolated from vertex intensities');
 assert.deepEqual(plain(bed.colorscale),[[0,'#75e3d7'],[0.15,'#58d2e2'],[0.35,'#39b5e7'],[0.6,'#2b91df'],[0.8,'#236bd2'],[1,'#173fbd']],
  'bed uses the depth palette rather than the selected field palette');
 assert.equal(bed.cmin,0,'bed colors begin at zero metres');
 assert.equal(bed.cmax,8,'bed colors end at the geometry maximum depth in metres');
 assert.deepEqual(plain(bed.intensity),plain(geometry.floor.intensity),'bed depth samples remain unchanged while their display range is corrected');
 const rendered=env(d);await rendered.context.render3DWaterBody('temp',0,{level:0,ve:100,showLand:false,showBedSurface:true});
 const renderedBed=rendered.plots[0].traces.find(trace=>trace.meta?.waterbodyFrame==='bed');
 assert.ok(renderedBed,'high-VE rendered bathymetry retains a bed trace');
 assert.equal(renderedBed.color,undefined,'rendered bed must not use Plotly mesh3d direct color');
 assert.equal(renderedBed.intensitymode,'vertex');
 assert.deepEqual(plain(renderedBed.intensity),plain(renderedBed.customdata));
 assert.deepEqual(plain(renderedBed.colorscale),plain(bed.colorscale));
 assert.equal(renderedBed.cmin,0);
 assert.equal(renderedBed.cmax,8);
 const field=rendered.plots[0].traces.find(trace=>trace.meta?.scientificField);
 assert.equal(field.cmin,10,'the scientific field retains its selected-variable minimum');
 assert.equal(field.cmax,25,'the scientific field retains its selected-variable maximum');
});

test('dynamic and default static previews hide the bed while retaining the water surface and boundary walls',async()=>{
 const d={shape:[1,2,2],xc:[0,100],yc:[0,100],bottom:[[2,4],[6,8]],water_depth:[[2,4],[6,8]],
  depth:[[[1,2],[3,4]]],sigma:[-.5],data:[[[10,15],[20,25]]],min:10,max:25,units:'mg/L'};
 for(const ve of [50,100]){
  const e=env(d);await e.context.render3DWaterBody('temp',0,{level:0,ve,overlay:true,showLand:false});
  const traces=e.plots[0].traces;
  assert.ok(!traces.some(trace=>trace.meta?.waterbodyFrame==='bed'),'dynamic overlays must omit the bed mesh at low and high VE');
  assert.ok(traces.some(trace=>trace.meta?.scientificField),'dynamic overlays retain the scientific field');
  if(ve<=80)assert.ok(traces.some(trace=>trace.meta?.waterbodyFrame==='wall'),'low-VE shoreline section walls remain visible');
 }
 const stat=env({depth:[[0,5],[4,8]],xc:[0,1],yc:[0,1],dry_mask:[[true,false],[false,false]]});
 await stat.context.renderBathymetry3D({meshMode:'triangles'});
 const traces=stat.plots[0].traces;
 const bed=traces.find(trace=>trace.meta?.waterbodyFrame==='bed');
 const surface=traces.find(trace=>trace.meta?.waterbodyFrame==='surface');
 assert.equal(bed,undefined,'the basin floor stays hidden in the default static preview');
 assert.ok(surface&&surface.opacity===.58,'the stronger translucent blue water surface anchors the basin without hiding its side wall');
 assert.ok(traces.some(trace=>trace.meta?.waterbodyFrame==='wall'),'wet-grid sidewalls make water volume visible without a bed');
 assert.ok(traces.some(trace=>trace.meta?.shoreline),'static terrain retains shoreline context');
 assert.ok(traces.some(trace=>trace.meta?.coastalRim),'static terrain retains the coastal depth transition');
});

test('static bathymetry status explicitly identifies a schematic water surface and hidden basin',async()=>{
 const grid={nx:2,ny:2,xc:[0,1],yc:[0,1],depth:[[4,8],[12,0]],dry_mask:[[false,false],[false,true]],
  coordinate_mode:'projected',coordinate_units:'m'};
 const e=env(grid,grid);await e.context.renderBathymetry3D();
 const traces=e.plots[0].traces,bedIndex=traces.findIndex(trace=>trace.meta?.waterbodyFrame==='bed');
 const surfaceIndex=traces.findIndex(trace=>trace.meta?.waterbodyFrame==='surface');
 const featherIndex=traces.findIndex(trace=>trace.meta?.waterbodyFrame==='shorelineAntialias');
 const shorelineIndex=traces.findIndex(trace=>trace.meta?.shoreline===true);
 assert.equal(bedIndex,-1,'static bathymetry hides the bed by default');
 assert.ok(surfaceIndex>=0,'static bathymetry keeps the blue water surface');
 assert.ok(featherIndex>surfaceIndex&&shorelineIndex>featherIndex,
  'static coast feather and smoothed wet-grid outline stay visible around the water cap');
 assert.match(e.status.textContent,/(湖底隐藏.*半透明蓝色水面与湿网格侧壁展示体积|半透明蓝色水面与湿网格侧壁展示体积.*湖底隐藏)/);
});

test('waterbody renders a visible default water surface and only a topology-derived near-shore land fringe',async()=>{
 const n=7,wet=Array.from({length:n},(_,j)=>Array.from({length:n},(_,i)=>i>=2&&i<=4&&j>=2&&j<=4));
 const bottom=wet.map(row=>row.map(value=>value?5:0)),dry=wet.map(row=>row.map(value=>!value));
 const data={shape:[1,n,n],xc:Array.from({length:n},(_,i)=>i),yc:Array.from({length:n},(_,j)=>j),bottom,water_depth:bottom,
  wet_mask:wet,dry_mask:dry,depth:[bottom],sigma:[-.5],data:[bottom.map(row=>row.map(value=>value?3:null))],min:3,max:3,units:'mg/L'};
 const e=env(data),c=e.context,geometry=c.buildLakeGeometry(data.xc,data.yc,bottom),geometryBefore=plain(geometry);
 const staticTraces=c.lakeStaticTraces(geometry,data,{},null,'temp',false);
 assert.equal(staticTraces.surface.visible,true,'the waterbody must be visible in the default static rendering');
 assert.equal(staticTraces.surface.opacity,.78,'the neutral basin surface has a visible, restrained blue-cyan tint');
 const landCells=new Set(staticTraces.land.filter(trace=>trace.meta?.landPlane).flatMap(trace=>trace.cell.filter((_cell,index)=>index%4===0).map(cell=>cell.join(','))));
 assert.equal(landCells.size,16,'display context is limited to the eight-connected one-cell fringe around the 3x3 wet mask');
 assert.ok(!landCells.has('0,0'),'remote dry cells are not filled as a domain-wide land rectangle');
 assert.deepEqual(plain(geometry),geometryBefore,'shoreline and land presentation do not modify native wet-cell geometry');
 await c.render3DWaterBody('temp',0,{level:0,ve:100,overlay:true});
 const dynamicTraces=e.plots[0].traces,water=dynamicTraces.find(trace=>trace.name==='水面');
 assert.equal(water.visible,true,'dynamic rendering uses the same visible waterbody surface');
 assert.equal(water.opacity,.36,'dynamic variable overlays retain a visible water tint while revealing the scientific field');
 assert.ok(dynamicTraces.some(trace=>trace.meta?.scientificField),'the selected scientific variable remains visible above the translucent water surface');
 const fieldIndex=dynamicTraces.findIndex(trace=>trace.meta?.scientificField);
 const featherIndex=dynamicTraces.findIndex(trace=>trace.meta?.waterbodyFrame==='shorelineAntialias');
 const shorelineIndex=dynamicTraces.findIndex(trace=>trace.meta?.shoreline===true);
 assert.ok(featherIndex>fieldIndex,'the softened boundary is composited after the dynamic scientific field');
 assert.ok(shorelineIndex>featherIndex,'the smoothed wet-mask outline remains readable above the feather');
 assert.equal(dynamicTraces[featherIndex].meta.featherFraction,.48);
 assert.equal(dynamicTraces[featherIndex].meta.geographicPrecision,false);
 assert.ok(!dynamicTraces.some(trace=>trace.meta?.waterbodyFrame==='bed'),'the bed remains hidden by default');
});

test('static trace cache keeps static and dynamic water-surface opacity policies separate',()=>{
 const c=env().context,geometry=c.buildLakeGeometry([0,1],[0,1],[[4,4],[4,4]]);
 geometry.playbackTopologyKey='verified-topology';
 const data={static_geometry_key:'static-grid',coordinate_mode:'projected',coordinate_units:'m'};
 const identity={path:'case-a',name:'case-a',revision:1,outputRevision:1};
 const staticSurface=c.lakeStaticTraces(geometry,data,{},identity,'temp',false).surface;
 const dynamicSurface=c.lakeStaticTraces(geometry,data,{dynamicOverlay:true},identity,'temp',false).surface;
 assert.equal(staticSurface.opacity,.78);
 assert.equal(dynamicSurface.opacity,.36,'dynamic overlay uses its own visible tint instead of inheriting the cached static opacity');
});

test('shoreline feather is broader, stays inside confirmed wet cells, and leaves native geometry unchanged',()=>{
 const c=env().context,geometry=c.buildLakeGeometry([0,1],[0,1],[[4,4],[4,4]]),before=plain(geometry);
 const feather=c.lakeShorelineFeatherTrace(geometry);
 assert.ok(feather,'confirmed wet-cell boundaries receive a display-only feather');
 assert.equal(feather.meta.featherFraction,.48,'the feather reaches almost to wet-cell centers to reduce the hard raster edge');
 assert.equal(feather.meta.geographicPrecision,false,'the softened edge is not presented as a geographic shoreline');
 assert.ok(feather.vertexcolor.includes('rgba(247,250,251,1)'), 'the outer raster edge blends fully into the plot background for antialiasing');
 const midpointY=(geometry.walls.py[0]+geometry.walls.py[2])/2;
 const halfCell=.5;
 assert.ok(Math.abs((feather.y[3]-midpointY)/halfCell-.48)<1e-10,
  'the feather reaches 48% of a wet-cell half-width rather than remaining a narrow pixel rim');
 const staticTraces=c.lakeStaticTraces(geometry,{}, {}, null,'',false);
 assert.equal(staticTraces.shoreline.line.width,2.2,'generalized shoreline remains visible against the native wet-cell fill');
 assert.equal(staticTraces.shoreline.line.color,'#5b98a3','shoreline stroke uses a restrained but legible water-adjacent tint');
 assert.equal(staticTraces.shoreline.meta.geographicPrecision,false,'display contour must not claim geographic precision');
 assert.deepEqual(plain(geometry),before,'shoreline smoothing never mutates solver or native wet-mask geometry');
});

test('initial lake viewport fits the full wet-cell bounds with a measured near-shore land margin',()=>{
 const e=env(),scene=e.context.lakeScene(1,20,{xc:[0,10,20,30,40],yc:[0,10,20,30],
  bottom:[[0,0,0,0,0],[0,3,3,3,0],[0,3,3,3,0],[0,0,0,0,0]],
  wet_mask:[[false,false,false,false,false],[false,true,true,true,false],[false,true,true,true,false],[false,false,false,false,false]]});
 assert.ok(plain(scene.xaxis.range).every((value,i)=>Math.abs(value-[-.4,40.4][i])<1e-10));
 assert.ok(plain(scene.yaxis.range).every((value,i)=>Math.abs(value-[1.4,28.6][i])<1e-10));
 assert.equal(scene.xaxis.autorange,false);assert.equal(scene.yaxis.autorange,false);
 const wetX=30,visibleX=scene.xaxis.range[1]-scene.xaxis.range[0];
 assert.ok(wetX/visibleX>=.70&&wetX/visibleX<=.75,'wet-cell bounds occupy roughly 70% of the view width before viewport projection');
 assert.equal(scene.camera.projection.type,'orthographic','fitted lake view retains the orthographic projection');
 const reversed=e.context.lakeScene(1,20,{xc:[40,30,20,10,0],yc:[30,20,10,0],
  bottom:[[0,0,0,0,0],[0,3,3,3,0],[0,3,3,3,0],[0,0,0,0,0]],wet_mask:[[false,false,false,false,false],
   [false,true,true,true,false],[false,true,true,true,false],[false,false,false,false,false]]});
 assert.ok(reversed.xaxis.range.every((value,i)=>Math.abs(value-[-.4,40.4][i])<1e-10),'descending coordinate grids keep the same physical view bounds');
 assert.ok(reversed.yaxis.range.every((value,i)=>Math.abs(value-[1.4,28.6][i])<1e-10));
 const edge=e.context.lakeScene(1,20,{xc:[0,10],yc:[0,10],bottom:[[3,3],[3,3]]});
 assert.ok(Math.abs(edge.xaxis.range[0]-(-8.6))<1e-10&&Math.abs(edge.xaxis.range[1]-18.6)<1e-10,
  'a basin reaching the native grid edge keeps its wet-cell bounds and receives blank plot margin outside the sampled domain');
 assert.ok(Math.abs(edge.yaxis.range[0]-(-8.6))<1e-10&&Math.abs(edge.yaxis.range[1]-18.6)<1e-10,
  'the edge-connected basin retains equal framing margins on the other horizontal axis');
});

test('automatic lake relief is clearly visible while explicit vertical exaggeration stays exact',()=>{
 const c=env().context,auto=c.lakeVerticalScale([0,8000],[0,4000],[[4,8],[12,20]],0);
 assert.ok(auto>=10,'automatic relief should keep shallow water legible without making vertical relief dominate the basin');
 const dianchiX=Array.from({length:41},(_,i)=>i*500),dianchiY=Array.from({length:82},(_,j)=>j*500);
 const dianchiDepth=Array.from({length:82},()=>Array(41).fill(7.748));
 const dianchiAuto=c.lakeVerticalScale(dianchiX,dianchiY,dianchiDepth,0);
 assert.ok(dianchiAuto>=150&&dianchiAuto<=250,'the Dianchi-like lake must not inherit an extreme automatic vertical exaggeration');
 const dianchiScene=c.lakeScene(dianchiAuto,7.748,{xc:dianchiX,yc:dianchiY,bottom:dianchiDepth});
 const reliefRatio=dianchiScene.aspectratio.z/dianchiScene.aspectratio.y;
 assert.ok(reliefRatio>=.025&&reliefRatio<=.035,
  'auto scale keeps Dianchi relief near 3% of the longest horizontal span while preserving a readable volume');
 assert.equal(c.lakeVerticalScale([0,8000],[0,4000],[[4,8],[12,20]],15),15);
});

test('high-resolution triangular network obeys its display-edge budget',()=>{
 const c=env().context,n=120,mesh={x:[],y:[],z:[],cell:[]};
 for(let j=0;j<n;j++)for(let i=0;i<n;i++)for(const [x,y] of [[i,j],[i+1,j],[i+1,j+1],[i,j+1]]){
  mesh.x.push(x);mesh.y.push(y);mesh.z.push(0);mesh.cell.push([i,j]);
 }
 const network=c.buildLakeGrid({floor:mesh,nx:n,ny:n},{mode:'triangles',density:1});
 assert.ok(network.stats.segments<=network.stats.maxSegments,'network trace count must have a firm upper bound on dense grids');
 assert.ok(network.stats.density>=1);
});

test('82-by-41 static lake keeps the full fine triangle lattice and lifts it clear of the bed',()=>{
 const c=env().context,nx=41,ny=82,xc=Array.from({length:nx},(_,i)=>i*500),yc=Array.from({length:ny},(_,j)=>j*500);
 const bottom=Array.from({length:ny},(_,j)=>Array.from({length:nx},(_,i)=>{
  const r=((i-20)/20)**2+((j-40)/19)**2;return r<1?1+6*(1-r):null;
 }));
 const ve=c.lakeVerticalScale(xc,yc,bottom),g=c.buildLakeGeometry(xc,yc,bottom,ve);
 const raw=c.buildLakeGrid(g,{mode:'triangles',density:1}),topologyData=fixtureTopology({shape:[1,ny,nx],xc,yc,bottom}),line=c.lakeDisplayLines(g.floor,g,{meshMode:'triangles'},topologyData)[0];
 assert.equal(raw.stats.density,1,'a medium lake under the line budget must not have missing checkerboard cells');
 assert.equal(raw.stats.refinement,3,'the subdivision level may fall only as needed to stay under the edge budget');
 assert.ok(raw.stats.segments>30000,'the reference mesh remains a dense connected triangular network on real-sized grids');
 assert.ok(line.line.width<=2.5&&line.opacity<=.9,'fine wire edges remain visible without covering the bathymetry fill');
 assert.ok(line.meta.displayLift>=g.maxDepth*ve*.009,'wire overlay must be lifted enough to avoid depth-buffer flicker');
 const q=line.x.findIndex(Number.isFinite),r=raw.x.findIndex(Number.isFinite);
 assert.ok(Math.abs((line.z[q]-raw.z[r])-line.meta.displayLift)<1e-8,'line z values stay exactly on the generated bed network plus a uniform display-only lift');
});

test('static preview is labeled as water and keeps the bed hidden by default',async()=>{
 const data={xc:[0,1],yc:[0,1],depth:[[1,4],[8,2]],display_topology:null};
 const e=env(data);let published;
 e.context.window.ScientificWorkspace={publish:(surface,meta)=>{published={surface,meta};}};
 await e.context.renderBathymetry3D({});
 const traces=e.plots[0].traces;
 assert.ok(traces.some(trace=>trace.meta?.waterbodyFrame==='surface'),'static preview includes its water surface');
 const wall=traces.find(trace=>trace.meta?.waterbodyFrame==='wall');
 assert.ok(wall,'static preview shows a volume cue');
 const ve=e.context.lakeVerticalScale(data.xc,data.yc,data.depth,0);
 assert.ok(new Set(wall.z.filter(z=>z<0)).size>1,'wall feet reflect varying source wet-cell depths');
 assert.ok(Math.min(...wall.z)<-ve,'volume extends beyond the shallowest wet cell');
 assert.match(e.graph._viz3dLastPlot.detail,/侧壁仅作体积示意.*不代表岸缘实测水深/);
 assert.ok(!traces.some(trace=>trace.meta?.waterbodyFrame==='bed'),'default static preview keeps the bed hidden');
 assert.equal(published?.meta?.label,'静态水体预览','status metadata describes the water-first view, not a visible lake bed');
 assert.match(e.graph._viz3dLastPlot.detail,/水面与.*展示体积/);
});

test('static bathymetry keeps its triangular overlay and adds low-profile display-only wet-mask walls',async()=>{
 const depth=[[0,0,0,0,0],[0,5,8,4,0],[0,7,12,6,0],[0,0,0,0,0]];
 const g={depth,xc:[0,1,2,3,4],yc:[0,1,2,3],dry_mask:depth.map(row=>row.map(v=>v===0)),
  coordinate_mode:'projected',coordinate_units:'m'};
 const e=env(g);await e.context.renderBathymetry3D({meshMode:'triangles',showBedSurface:true,ve:300});
 const traces=e.plots[0].traces,floor=traces.findIndex(t=>t.meta?.waterbodyFrame==='bed');
 const network=traces.find(t=>t.meta?.displayOnly&&t.meta?.networkMode==='triangles');
 assert.ok(floor>=0&&network,'static depth surface must get its own triangle-wire overlay');
 assert.ok(traces.indexOf(network)>floor,'triangle wires render above the colored lake bed');
 const wall=traces.find(t=>t.meta?.waterbodyFrame==='wall');
 assert.ok(wall,'static bathymetry must retain a waterbody wall at high vertical exaggeration');
 assert.equal(wall.meta.displayOnly,true);assert.equal(wall.meta.source,'wet-mask-boundary');
 assert.equal(wall.opacity,.28,'static walls use restrained contrast so depth-sampled edge detail does not dominate the lake');
 assert.equal(wall.intensity,undefined);assert.equal(wall.showscale,false,'wall does not encode depth values');
 assert.ok(Math.min(...wall.z)>=-.12*4-1e-8,'high VE walls are limited relative to the horizontal lake span');
 assert.ok(new Set(wall.z.filter(z=>z<0)).size>1,'the display limit retains relative source depth variation');
 assert.ok(wall.meta.wallDepthLimitM<4,'the geometric display cap prevents high VE curtains');
 assert.ok(!traces.some(t=>/ · 层 /.test(t.name||'')),'static preview must not show scattered model layers');
 assert.ok(traces.some(t=>t.meta?.displayOnly&&t.meta?.shoreline),'smoothed shoreline remains an independent display trace');
});

test('every confirmed wet coastal face gets a finite blue depth colour; mixed and unknown mask cells stay absent',async()=>{
 const depth=[[null,3,0],[2,5,null],[0,4,6]],topology={
  contract:'sampled-wet-topology-v1',source_shape:[3,3],x_indices:[0,1,2],y_indices:[0,1,2],sampling_stride:[1,1],
  grid_hash:'sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',mask_cells_examined:9,
  x_edges:[-.5,.5,1.5,2.5],y_edges:[-.5,.5,1.5,2.5],
  cell_status:[['unknown','wet','dry'],['wet','wet','mixed'],['dry','wet','wet']],
  wet_mask:[[false,true,false],[true,true,false],[false,true,true]],
  land_mask:[[false,false,true],[false,false,false],[true,false,false]],
  wall_sides:[[[false,false,false,false],[false,true,false,false],[false,false,false,false]],
   [[false,false,true,false],[false,false,false,false],[false,false,false,false]],
   [[false,false,false,false],[false,false,false,true],[false,false,false,false]]],mixed_or_unknown_cells:2
 };
 const g={depth,xc:[0,1,2],yc:[0,1,2],dry_mask:depth.map(row=>row.map(v=>v===0)),display_topology:topology};
 const e=env(g);await e.context.renderBathymetry3D({meshMode:'triangles',showBedSurface:true});
 const traces=e.plots[0].traces,floor=traces.find(t=>t.meta?.waterbodyFrame==='bed');
 assert.equal(floor.i.length,10,'each of five verified wet coast/interior cells contributes two triangles');
 assert.equal(floor.intensitymode,'vertex','triangle vertices retain the documented smooth depth interpolation across verified wet cells');
 assert.equal(floor.intensity.length,floor.x.length,'every confirmed wet triangle vertex has a finite depth colour');
 assert.ok(floor.intensity.every(v=>Number.isFinite(v)&&v>0&&v<=6),'wet face colours use only real positive depth values');
 assert.ok(!traces.some(t=>t.meta?.landPlane),'known dry cells do not form a square land plane without elevation data');
 assert.ok(traces.some(t=>t.meta?.coastalRim),'verified shoreline edges keep their display-only coastal rim');
 assert.ok(!floor.cell?.some(([i,j])=>topology.cell_status[j][i]!=='wet'),'unknown/mixed/dry cells never become coloured water faces');
});

test('static coastal rim closes only verified wet-to-land edges and never bridges mixed or unknown cells',async()=>{
 const depth=[[null,3,0],[2,5,null],[0,4,6]],topology={
  contract:'sampled-wet-topology-v1',source_shape:[3,3],x_indices:[0,1,2],y_indices:[0,1,2],sampling_stride:[1,1],
  grid_hash:'sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',mask_cells_examined:9,
  x_edges:[-.5,.5,1.5,2.5],y_edges:[-.5,.5,1.5,2.5],
  cell_status:[['unknown','wet','dry'],['wet','wet','mixed'],['dry','wet','wet']],
  wet_mask:[[false,true,false],[true,true,false],[false,true,true]],
  land_mask:[[false,false,true],[false,false,false],[true,false,false]],
  wall_sides:[[[false,false,false,false],[false,true,false,false],[false,false,false,false]],
   [[false,false,true,false],[false,false,false,false],[false,false,false,false]],
   [[false,false,false,false],[false,false,false,true],[false,false,false,false]]],mixed_or_unknown_cells:2
 };
 const e=env({depth,xc:[0,1,2],yc:[0,1,2],dry_mask:depth.map(row=>row.map(v=>v===0)),display_topology:topology});
 await e.context.renderBathymetry3D({meshMode:'triangles'});
 const rim=e.plots[0].traces.find(t=>t.meta?.coastalRim);
 assert.ok(rim,'a blue-cyan edge skirt fills the visible gap between the verified lake bed and known land');
 assert.equal(rim.i.length,6,'only three wet-to-verified-land sides get two rim triangles each');
 assert.equal(rim.intensitymode,'vertex');assert.equal(rim.intensity.length,rim.x.length);
 for(let q=0;q<rim.cell.length;q+=4){
  const [i,j]=rim.cell[q],neighbours=[[i,j-1],[i+1,j],[i,j+1],[i-1,j]];
  assert.ok(neighbours.some(([x,y])=>topology.land_mask[y]?.[x]===true),'each rim quad borders a verified dry cell');
  assert.ok(topology.wet_mask[j][i],'each rim quad starts from a confirmed wet cell');
 }
 assert.ok(rim.intensity.every(v=>Number.isFinite(v)&&v>=0),'the rim uses only finite bed depths and the known zero water-surface datum');
 const geometry=e.context.buildLakeGeometry([0,1,2],[0,1,2],depth.map(row=>row.map(v=>Number.isFinite(v)&&v>0?v:0)),1,topology);
 assert.deepEqual(plain([rim.x,rim.y,rim.z]),plain([geometry.walls.px,geometry.walls.py,geometry.walls.pz]),
  'coastal fill must be derived from actual wet-cell boundary walls');
});

test('static blue rim never colors an outer-domain, mixed, or unknown boundary',()=>{
 const c=env().context,depth=[[4,4],[4,0]],d={xc:[0,1],yc:[0,1],depth,dry_mask:[[false,false],[false,true]]};
 const geometry=c.buildLakeGeometry(d.xc,d.yc,depth),rim=c.buildLakeCoastalRim(geometry,d);
 const edges=new Set();
 for(let q=0;q<rim.x.length;q+=4)edges.add([rim.x[q],rim.y[q],rim.x[q+2],rim.y[q+2]].join(','));
 assert.equal(edges.size,2,'only internal edges facing the explicitly dry cell may receive a blue skirt');
 assert.equal(c.buildLakeCoastalRim(geometry,{...d,dry_mask:[[false,false],[false,false]]}).i.length,0,
  'a neighbor without explicit dry evidence cannot be painted as shore');
});

test('land reference limits display-only terrain to the verified near-shore fringe',()=>{
 const c=env().context,n=11,wetMask=Array.from({length:n},(_,j)=>Array.from({length:n},(_,i)=>i>=4&&i<=6&&j>=4&&j<=6));
 const dry=wetMask.map(row=>row.map(v=>!v));dry[0][0]=false;
 const data={xc:Array.from({length:n},(_,i)=>i),yc:Array.from({length:n},(_,j)=>j),
  wet_mask:wetMask,dry_mask:dry,bottom:wetMask.map((row,j)=>row.map((v,i)=>j===0&&i===0?null:(v?5:0)))};
 const land=c.buildLakeLand(data),cells=new Set();
 for(let q=0;q<land.cell.length;q+=4)cells.add(land.cell[q].join(','));
 assert.equal(cells.size,16,'only explicitly dry cells in the eight-connected fringe around wet cells provide display context');
 assert.ok(!cells.has('0,0'),'unknown bathymetry must not be reclassified as land');
 for(let j=0;j<n;j++)for(let i=0;i<n;i++)if(wetMask[j][i])assert.ok(!cells.has(`${i},${j}`),'wet cells remain reserved for blue water rendering');
});

test('verified land context omits remote dry cells and never colors unknown or wet cells',()=>{
 const c=env().context,n=7,wet=Array.from({length:n},(_,j)=>Array.from({length:n},(_,i)=>i>=2&&i<=4&&j>=2&&j<=4));
 const dry=wet.map(row=>row.map(v=>!v));dry[0][0]=false;
 const land=c.buildLakeLand({xc:Array.from({length:n},(_,i)=>i),yc:Array.from({length:n},(_,j)=>j),
  bottom:wet.map(row=>row.map(v=>v?5:0)),wet_mask:wet,dry_mask:dry});
 const cells=new Set();for(let q=0;q<land.cell.length;q+=4)cells.add(land.cell[q].join(','));
 assert.equal(cells.size,16,'only dry cells adjacent to the wet shoreline provide display context');
 assert.ok(!cells.has('0,0'),'a cell without explicit dry evidence must stay transparent');
 for(let j=0;j<n;j++)for(let i=0;i<n;i++)if(wet[j][i])assert.ok(!cells.has(`${i},${j}`),'verified water cannot be painted as land');
});

test('smoothed shoreline rounds display corners without changing native wet geometry',()=>{
 const c=env().context,before=[[5,5,0],[5,5,0],[0,0,0]],g=c.buildLakeGeometry([0,1,2],[0,1,2],before),raw=plain(g.shoreline);
 const threePass=c.smoothLakeShoreline(g.shoreline,3),smooth=c.smoothLakeShoreline(g.shoreline),points=smooth.x.filter(Number.isFinite).length;
 assert.ok(points>threePass.x.filter(Number.isFinite).length,
  'the generalized display contour receives an additional corner-cutting pass');
 const rawVertices=new Set();for(let q=0;q+1<raw.x.length;q+=3)if(Number.isFinite(raw.x[q])){rawVertices.add(`${raw.x[q]},${raw.y[q]}`);rawVertices.add(`${raw.x[q+1]},${raw.y[q+1]}`);}
 assert.ok(points>rawVertices.size,'corner smoothing should add interpolated shoreline points');
 assert.ok(smooth.x.every(v=>v===null||v>=-.5&&v<=2.5));assert.ok(smooth.y.every(v=>v===null||v>=-.5&&v<=2.5));
 assert.deepEqual(plain(g.shoreline),raw,'shoreline smoothing is display-only and leaves the native mask geometry untouched');
 const firstDiagonal=Array.from({length:smooth.x.length-1},(_,i)=>i).find(i=>Number.isFinite(smooth.x[i])&&Number.isFinite(smooth.x[i+1])&&
  Math.abs(smooth.x[i+1]-smooth.x[i])>1e-8&&Math.abs(smooth.y[i+1]-smooth.y[i])>1e-8);
 assert.ok(Number.isInteger(firstDiagonal),'corner interpolation rounds the staircase with visible diagonal/curved display segments');
 const origin=raw.x.findIndex(v=>v===0);assert.notEqual(smooth.x[0],0,'standard corner cutting moves the display shoreline more than a negligible fraction of one cell');
});
test('uploaded shoreline proxy stays explicitly labeled and keeps its geographic shape',()=>{
 const c=env().context,g=c.buildLakeGeometry([0,1,2],[0,1,2],[[5,5,5],[5,5,5],[5,5,5]]);
 const source={authoritative_boundary:{source_crs:'case projected CRS',projected_polygons:[{outer:[[0,0],[2.5,0],[2.5,2.5],[0,2.5],[0,0]],holes:[]}],
  provenance:{source:'recovered-local-upload-cache',status:'proxy-display-geometry-not-scientifically-validated'}}};
 const trace=c.lakeShorelineTrace(g,source);
 assert.match(trace.name,/recovered-local-upload-cache.*显示代理.*地理\/科学真实性未验证/,'unvalidated provenance must remain visible in the rendered legend');
 assert.deepEqual(plain([trace.x[0],trace.y[0],trace.x[1],trace.y[1]]),[0,0,2.5,0],
  'an uploaded outline should preserve its source vertices rather than smoothing them into invented geography');
 assert.equal(trace.meta.displayOnly,true);
 assert.equal(trace.meta.geographicPrecision,null);
});
test('a saved source outline remains explicitly unverified after coordinate and mask checks',()=>{
 const c=env().context,g=c.buildLakeGeometry([0,1,2],[0,1,2],[[5,5,0],[5,5,0],[0,0,0]]);
 const data={xc:[0,1,2],yc:[0,1,2],wet_mask:[[true,true,false],[true,true,false],[false,false,false]],
  dry_mask:[[false,false,true],[false,false,true],[true,true,true]],
  authoritative_boundary:{source_crs:'case projected CRS',projected_crs:{wkt:'case projected CRS'},
   coordinate_space:'bathymetry_projected_grid_coordinates',
   projected_polygons:[{outer:[[-.5,-.5],[1.5,-.5],[1.5,1.5],[-.5,1.5],[-.5,-.5]],holes:[]}],
   provenance:{source:'uploaded-boundary-shapefile'}}};
 const trace=c.lakeShorelineTrace(g,data);
 assert.match(trace.name,/uploaded-boundary-shapefile.*显示代理.*地理\/科学真实性未验证/,
  'CRS, source, and mask consistency establish display eligibility only');
 assert.match(c.lakeDisplayBoundaryStatus(g,data),/坐标\/湿干掩膜一致性检查仅用于显示裁切；地理\/科学真实性未验证/,
  '3D status explains that matching checks do not validate real-world geography');
});
test('an uploaded outline with only a sliver of grid overlap is rejected',()=>{
 const c=env().context,g=c.buildLakeGeometry([0,1,2],[0,1,2],[[5,5,5],[5,5,5],[5,5,5]]);
 const sliver={authoritative_boundary:{source_crs:'case projected CRS',projected_polygons:[{outer:[[2.49,0],[3,0],[3,2.5],[2.49,2.5]],holes:[]}],provenance:{source:'uploaded-boundary-shapefile'}}};
 const trace=c.lakeShorelineTrace(g,sliver);
 assert.equal(trace.meta.source,'native-wet-mask-boundary-display-generalization',
  'a boundary whose bbox only barely touches the wet-grid extent is not spatially validated');
});test('malformed or spatially unrelated shoreline falls back to the native wet-mask outline',()=>{
 const c=env().context,g=c.buildLakeGeometry([10,11,12],[20,21,22],[[5,5,5],[5,5,5],[5,5,5]]);
 const unrelated={authoritative_boundary:{projected_polygons:[{outer:[[100,100],[101,100],[101,101],[100,101]],holes:[]}],provenance:{source:'uploaded-boundary-shapefile'}}};
 const malformed={authoritative_boundary:{projected_polygons:[{outer:[[null,20],[11,20],[11,21]],holes:[]}],provenance:{source:'uploaded-boundary-shapefile'}}};
 for(const data of [unrelated,malformed]){
  const trace=c.lakeShorelineTrace(g,data);
  assert.equal(trace.meta.source,'native-wet-mask-boundary-display-generalization',
   'invalid or non-overlapping boundary metadata must not displace the actual wet topology');
  assert.ok(trace.x.some(Number.isFinite),'the native wet outline remains available as a visible fallback');
 }
});
test('validated display proxy clips only presentation vertices to its natural polygon',()=>{
 const c=env().context,geometry=c.buildLakeGeometry([.5,1.5],[.5,1.5],[[5,5],[5,0]]);
 const wet=[[true,true],[true,false]],dry=[[false,false],[false,true]];
 const polygon={outer:[[0,0],[2,0],[2,.75],[.75,.75],[.75,2],[0,2],[0,0]],holes:[]};
 const data={xc:[.5,1.5],yc:[.5,1.5],wet_mask:wet,dry_mask:dry,
  authoritative_boundary:{source_crs:{wkt:'retained-case-metadata-only'},projected_crs:{wkt:'retained-case-metadata-only'},coordinate_space:'bathymetry_projected_grid_coordinates',
   projected_polygons:[polygon],provenance:{source:'recovered-local-upload-cache',status:'proxy-display-geometry-not-scientifically-validated'}}};
 const source={x:[],y:[],z:[],intensity:[],customdata:[],cell:[],i:[],j:[],k:[]};
 for(let q=0;q<geometry.floor.x.length;q+=4){
  const [i,j]=geometry.floor.cell[q],b=source.x.length;for(let n=0;n<4;n++){
   const x=geometry.floor.x[q+n],y=geometry.floor.y[q+n],v=n+1;
   source.x.push(x);source.y.push(y);source.z.push(v);source.intensity.push(v);source.customdata.push([5,0,i+.5,j+.5,i,j,v]);source.cell.push([i,j]);
  }
  source.i.push(b,b);source.j.push(b+1,b+2);source.k.push(b+2,b+3);
 }
 const clipped=c.lakeClipMeshToBoundary(source,geometry,data);
 assert.ok(clipped,'a center-validated proxy should produce a display-only clipped mesh');
 assert.equal(clipped.cell.length,clipped.x.length,'every clipped display vertex retains its original source-cell key');
 assert.ok(clipped.x.every((x,n)=>x>=0&&x<=2&&clipped.y[n]>=0&&clipped.y[n]<=2));
 assert.ok(clipped.i.length>0,'the clipped mesh remains visible');
 assert.ok(clipped.cell.every(([i,j])=>wet[j][i]),'clipping cannot introduce cells outside the native wet mask');
 assert.equal(source.x.length,geometry.floor.x.length,'the original render mesh remains unchanged');
 assert.ok(clipped.customdata.every(row=>row[4]===clipped.cell[clipped.customdata.indexOf(row)]?.[0]),'hover rows remain mapped to source cells');
 assert.equal(clipped.meta.wetTopologyUnchanged,true);assert.equal(clipped.meta.fieldValuesInterpolatedWithinNativeCell,true);
 const staticTraces=c.lakeStaticTraces(geometry,{...data,bottom:[[5,5],[5,0]]},{staticBathymetry:true},null,'depth',false);
 assert.ok(staticTraces.surface.x.length>geometry.surface.x.length,'polygon intersections subdivide static display faces while clipping edge cells');
 assert.match(staticTraces.shoreline.name,/recovered-local-upload-cache.*显示代理.*地理\/科学真实性未验证/,'the visible contour retains its proxy provenance label');
 const fieldData={...data,shape:[1,2,2],sigma:[-.5],bottom:[[5,5],[5,0]],depth:[[[5,5],[5,null]]],data:[[[1,2],[3,NaN]]],valid_geometry:[[true,true],[true,false]]};
 const fieldCorners=c.lakeLayerCornerAverages(geometry,fieldData,0,false);
 const nativeField=c.lakeLayerMeshes(geometry,fieldData,0,1,false,fieldCorners).fieldMesh;
 const clippedField=c.lakeClipMeshToBoundary(nativeField,geometry,fieldData);
 assert.ok(clippedField&&clippedField.x.length>nativeField.x.length,'dynamic field display subdivides and clips its outer faces');
 const sourceHover=new Map();for(let q=0;q<nativeField.cell.length;q+=4)sourceHover.set(JSON.stringify(plain(nativeField.cell[q])),plain(nativeField.customdata[q]));
 assert.ok(clippedField.cell.every((cell,index)=>{
  const expected=sourceHover.get(JSON.stringify(plain(cell)));
  return JSON.stringify(plain(clippedField.customdata[index]))===JSON.stringify(expected);
 }), 'dynamic hover data remains mapped to the original wet-cell measurement after display clipping');
});
test('validated proxy clipping still creates side walls along the clipped wet footprint',()=>{
 const c=env().context,xc=[.5,1.5],yc=[.5,1.5],bottom=[[5,0],[0,0]],geometry=c.buildLakeGeometry(xc,yc,bottom,1);
 const data={xc,yc,bottom,wet_mask:[[true,false],[false,false]],dry_mask:[[false,true],[true,true]],
  authoritative_boundary:{coordinate_space:'bathymetry_projected_grid_coordinates',
   projected_polygons:[{outer:[[.3,.3],[.7,.3],[.7,.7],[.3,.7],[.3,.3]],holes:[]}],
   provenance:{source:'recovered-local-upload-cache',status:'proxy-display-geometry-not-scientifically-validated'}}};
 const traces=c.lakeTraces(geometry,true,data,{min:0,max:5},{staticBathymetry:true,staticBasin:true,showBedSurface:true});
 const wall=traces.find(trace=>trace.meta?.waterbodyFrame==='wall');
 assert.ok(wall,'clipping the display surface must not suppress its waterbody side faces');
 assert.equal(wall.meta.source,'clipped-wet-surface-boundary');
 assert.ok(wall.x.every(x=>x>=.3-1e-9&&x<=.7+1e-9),'wall edges follow the proxy-clipped surface perimeter');
 assert.ok(wall.y.every(y=>y>=.3-1e-9&&y<=.7+1e-9),'walls do not overdraw beyond the clipped water footprint');
 assert.ok(wall.z.every(z=>z<=0&&z>=-5-1e-9),'wall feet stay within the source wet cell’s bathymetry');
 assert.equal(wall.i.length,8,'a closed clipped shoreline yields four side quads');
 const adjacentGeometry=c.buildLakeGeometry([.5,1.5,2.5],[.5,1.5],[[5,5,0],[0,0,0]],1);
 const adjacentData={xc:[.5,1.5,2.5],yc:[.5,1.5],bottom:[[5,5,0],[0,0,0]],
  wet_mask:[[true,true,false],[false,false,false]],dry_mask:[[false,false,true],[true,true,true]],
  authoritative_boundary:{coordinate_space:'bathymetry_projected_grid_coordinates',
   projected_polygons:[{outer:[[0,0],[2,0],[2,1],[0,1],[0,0]],holes:[]}],
   provenance:{source:'aligned-wet-mask-outline',status:'proxy-display-geometry-not-scientifically-validated'}}};
 const adjacentWall=c.lakeTraces(adjacentGeometry,true,adjacentData,{min:0,max:5},
  {staticBathymetry:true,staticBasin:true,showBedSurface:true}).find(trace=>trace.meta?.waterbodyFrame==='wall');
 assert.equal(adjacentWall.x.length/4,6,'adjacent clipped wet cells share one internal edge and expose only six outside edges');
 for(let q=0;q+3<adjacentWall.x.length;q+=4)
  assert.ok(!(adjacentWall.x[q]===1&&adjacentWall.x[q+2]===1&&adjacentWall.y[q]!==adjacentWall.y[q+2]),
   'shared edges between adjacent wet cells do not become interior walls');
});
test('clipped sidewalls follow only the outer ring across several adjacent wet cells',()=>{
 const c=env().context,xc=[.5,1.5,2.5,3.5],yc=[.5,1.5,2.5,3.5];
 const ring=[[.13,.17],[3.83,.17],[3.83,.93],[3.41,1.29],[3.03,1.63],[2.61,2.01],[2.19,2.39],[1.77,2.77],[1.31,3.19],[.81,3.39],[.13,3.39],[.13,.17]];
 const inside=(x,y)=>{let yes=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++)if((ring[i][1]>y)!==(ring[j][1]>y)&&x<(ring[j][0]-ring[i][0])*(y-ring[i][1])/(ring[j][1]-ring[i][1])+ring[i][0])yes=!yes;return yes;};
 const wet=yc.map(y=>xc.map(x=>inside(x,y))),dry=wet.map(row=>row.map(value=>!value));
 const bottom=wet.map(row=>row.map(value=>value?5:0));
 const geometry=c.buildLakeGeometry(xc,yc,bottom),data={xc,yc,bottom,wet_mask:wet,dry_mask:dry,
  authoritative_boundary:{coordinate_space:'bathymetry_projected_grid_coordinates',projected_polygons:[{outer:ring,holes:[]}],
   provenance:{source:'synthetic-aligned-boundary',status:'proxy-display-geometry-not-scientifically-validated'}}};
 assert.ok(c.lakeValidatedDisplayBoundary(geometry,data),'synthetic polygon must satisfy the existing display-boundary contract');
 const frame=c.lakeDisplayFrame(geometry,data);assert.equal(frame.boundaryClipApplied,true);
 const walls=frame.wallMesh;assert.ok(walls?.i?.length,'a multi-cell clipped footprint should retain a visible perimeter wall');
 const onRing=(x,y)=>ring.slice(0,-1).some((a,index)=>{const b=ring[index+1],dx=b[0]-a[0],dy=b[1]-a[1],cross=(x-a[0])*dy-(y-a[1])*dx;
   return Math.abs(cross)<1e-9&&x>=Math.min(a[0],b[0])-1e-9&&x<=Math.max(a[0],b[0])+1e-9&&y>=Math.min(a[1],b[1])-1e-9&&y<=Math.max(a[1],b[1])+1e-9;});
 for(let q=0;q+3<walls.x.length;q+=4){
  assert.ok(onRing(walls.x[q],walls.y[q])&&onRing(walls.x[q+2],walls.y[q+2]),
   'every sidewall top edge must lie on the clipped polygon perimeter, never on a wet-cell seam');
 }
 assert.equal(frame.shoreline.meta.provenance.source,'synthetic-aligned-boundary','the wall and shoreline retain the same display-only source');
});
test('display boundary clipping failure falls back to one coherent wet-grid surface, wall, and shoreline',()=>{
 const c=env().context,geometry=c.buildLakeGeometry([.5,1.5],[.5,1.5],[[5,5],[5,0]]);
 const data={xc:[.5,1.5],yc:[.5,1.5],bottom:[[5,5],[5,0]],wet_mask:[[true,true],[true,false]],
  dry_mask:[[false,false],[false,true]],authoritative_boundary:{coordinate_space:'bathymetry_projected_grid_coordinates',
   projected_polygons:[{outer:[[0,0],[2,0],[2,.75],[.75,.75],[.75,2],[0,2],[0,0]],holes:[]}],
   provenance:{source:'recovered-local-upload-cache',status:'proxy-display-geometry-not-scientifically-validated'}}};
 // Simulate an accepted candidate whose display mesh cannot be clipped (for
 // example, the clipping triangle budget or malformed display mesh contract).
 const brokenGeometry={...geometry,surface:{...geometry.surface,cell:[]}};
 const frame=c.lakeDisplayFrame(brokenGeometry,data);
 assert.equal(frame.boundaryClipApplied,false);
 assert.equal(frame.surface,brokenGeometry.surface,'fallback surface must remain the untouched native wet mesh');
 assert.match(frame.shoreline.name,/湿网格岸线（代理，未验证）/,'a failed candidate cannot leave its vector outline over the native mesh');
 assert.equal(frame.shoreline.meta.source,'native-wet-mask-boundary-display-generalization');
 assert.match(c.lakeDisplayBoundaryStatus(brokenGeometry,data),/湿网格岸线概化（代理，未验证）/,
  'the explanatory status must describe the same wet-grid fallback as the rendered geometry');
 const traces=c.lakeTraces(brokenGeometry,true,data,{min:0,max:5},{staticBathymetry:true,staticBasin:true});
 const wall=traces.find(trace=>trace.meta?.waterbodyFrame==='wall');
 assert.equal(wall.meta.source,'wet-mask-boundary','wall fallback must use the same native wet-grid footprint');
});
test('proxy clipping handles holes and disconnected polygons, but rejects CRS mismatch and uncontained dry centers',()=>{
 const c=env().context,geometry=c.buildLakeGeometry([.5,1.5,2.5],[.5,1.5,2.5],[[5,0,0],[5,0,0],[0,0,5]]);
 const base={xc:[.5,1.5,2.5],yc:[.5,1.5,2.5],wet_mask:[[true,false,false],[true,false,false],[false,false,true]],
  dry_mask:[[false,true,true],[false,true,true],[true,true,false]],authoritative_boundary:{source_crs:null,
   coordinate_space:'bathymetry_projected_grid_coordinates',provenance:{source:'recovered-local-upload-cache',status:'proxy-display-geometry-not-scientifically-validated'},
   projected_polygons:[{outer:[[0,0],[1,0],[1,2],[0,2],[0,0]],holes:[[[.2,.3],[.4,.3],[.4,.4],[.2,.4],[.2,.3]]]},
    {outer:[[2,2],[3,2],[3,3],[2,3],[2,2]],holes:[]}]}};
 const fullGeometry=c.buildLakeGeometry(base.xc,base.yc,[[5,0,0],[5,0,0],[0,0,5]]);
 const acceptedProxy=c.lakeValidatedDisplayBoundary(fullGeometry,base);
 assert.ok(acceptedProxy,'well-aligned wet and dry center samples accept multi-part polygons with holes');
 assert.equal(acceptedProxy.sourceCrs,null,'CRS text reused for display alignment is not promoted to verified source CRS');
 const acceptedDetail=c.lakeDisplayBoundaryStatus(fullGeometry,base);
 assert.match(acceptedDetail,/recovered-local-upload-cache.*显示代理裁切（坐标\/湿干掩膜一致性检查仅用于显示裁切；地理\/科学真实性未验证）/,
  'an accepted cached vector boundary is disclosed as an unvalidated display-only clipping proxy');
 const frame=c.lakeDisplayFrame(fullGeometry,base),wall=frame.wallMesh;
 assert.equal(frame.boundaryClipApplied,true,'multipart and holed polygon edges can close the clipped display wall');
 assert.ok(wall?.meta?.includesOuterAndHoleRings,'clipped walls explicitly identify the source polygon rings they use');
 const rings=base.authoritative_boundary.projected_polygons.flatMap(group=>[group.outer,...group.holes]);
 const onAnyRing=(x,y)=>rings.some(ring=>ring.some((a,index)=>{const b=ring[(index+1)%ring.length],dx=b[0]-a[0],dy=b[1]-a[1],cross=(x-a[0])*dy-(y-a[1])*dx;
  return Math.abs(cross)<1e-9&&x>=Math.min(a[0],b[0])-1e-9&&x<=Math.max(a[0],b[0])+1e-9&&y>=Math.min(a[1],b[1])-1e-9&&y<=Math.max(a[1],b[1])+1e-9;}));
 for(let q=0;q+3<wall.x.length;q+=4)assert.ok(onAnyRing(wall.x[q],wall.y[q])&&onAnyRing(wall.x[q+2],wall.y[q+2]),
  'outer, hole and multipart walls contain no internal wet-cell seams');
 const clipped=c.lakeClipMeshToBoundary(fullGeometry.floor,fullGeometry,base);
 assert.ok(clipped,'the multipart boundary clips the mesh');
 for(let q=0;q+3<clipped.x.length;q+=4){
  const cx=(clipped.x[q]+clipped.x[q+1]+clipped.x[q+2]+clipped.x[q+3])/4;
  const cy=(clipped.y[q]+clipped.y[q+1]+clipped.y[q+2]+clipped.y[q+3])/4;
  assert.ok(!(cx>.2&&cx<.4&&cy>.3&&cy<.4),'polygon holes must remain empty in the visible surface');
 }
 const rejected={...base,authoritative_boundary:{...base.authoritative_boundary,coordinate_space:undefined}};
 assert.equal(c.lakeValidatedDisplayBoundary(fullGeometry,rejected),null,
  'a proxy without CRS or an explicit grid-coordinate declaration is rejected');
 assert.match(c.lakeDisplayBoundaryStatus(fullGeometry,rejected),/湿网格岸线概化（代理，未验证）/,
  'a rejected vector outline falls back to the unvalidated wet-grid proxy wording');
 const mismatch={...base,coordinate_crs_wkt:'different projected CRS'};
 mismatch.authoritative_boundary={...base.authoritative_boundary,source_crs:'EPSG source',projected_crs:{wkt:'projected CRS'},
  provenance:{source:'uploaded-boundary-shapefile',status:'validated-uploaded-boundary'}};
 assert.equal(c.lakeValidatedDisplayBoundary(fullGeometry,mismatch),null,'an explicit projected CRS mismatch disables clipping');
});
test('display clipping falls back as a whole when its triangle budget is exceeded',()=>{
 const c=env().context,geometry=c.buildLakeGeometry([.5,1.5],[.5,1.5],[[5,5],[5,0]]);
 const data={xc:[.5,1.5],yc:[.5,1.5],wet_mask:[[true,true],[true,false]],dry_mask:[[false,false],[false,true]],
  authoritative_boundary:{coordinate_space:'bathymetry_projected_grid_coordinates',projected_polygons:[{outer:[[0,0],[2,0],[2,.75],[.75,.75],[.75,2],[0,2],[0,0]],holes:[]}],
   provenance:{source:'recovered-local-upload-cache',status:'proxy-display-geometry-not-scientifically-validated'}}};
 const mesh={x:[],y:[],z:[],cell:[],customdata:[],i:[],j:[],k:[]};
 for(let q=0;q<100001;q++){const b=mesh.x.length;mesh.x.push(.5,.75,.75,.5);mesh.y.push(.5,.5,.75,.75);mesh.z.push(1,1,1,1);mesh.cell.push([0,0],[0,0],[0,0],[0,0]);mesh.customdata.push([0],[0],[0],[0]);mesh.i.push(b,b);mesh.j.push(b+1,b+2);mesh.k.push(b+2,b+3);}
 assert.equal(c.lakeClipMeshToBoundary(mesh,geometry,data),null,'an over-budget clip rejects the entire result and callers retain the original mesh');
 assert.equal(mesh.i.length,200002,'budget fallback does not mutate native display topology');
});
test('3D lake scene keeps axes while hiding competing scene gridlines',()=>{
 const c=env().context,scene=c.lakeScene(1,6,{xc:[0,1,2],yc:[0,1,2],bottom:[[0,0,0],[0,5,0],[0,0,0]]});
 assert.equal(scene.xaxis.showgrid,false);
 assert.equal(scene.yaxis.showgrid,false);
 assert.equal(scene.zaxis.showgrid,false);
 assert.ok(scene.xaxis.showline&&scene.yaxis.showline&&scene.zaxis.showline,'axis frame remains visible without gridlines');
 assert.ok(scene.xaxis.showline&&scene.yaxis.showline&&scene.zaxis.showline,
  'axis frames remain available for coordinate orientation');
});
test('selected missing colour stays a separate material in water, cloud and iso modes',async()=>{
 for(const mode of ['water','cloud','iso']){
  const e=env(mode==='iso'?{...payload,data:[[[null,null],[null,null]]],min:null,max:null}:payload);e.context.window.ScientificStyle={resolve:()=>({min:1,max:1,nanColor:'#e100a8',colorscale:[[0,'#000000'],[1,'#ffffff']],tickvals:[1],ticktext:['1']})};
  if(mode==='water')await e.context.render3DWaterBody('x',0,{level:0});else if(mode==='cloud')await e.context.render3DCloud('x',0);else await e.context.render3DSurface('x',0);
  const t=e.plots[0].traces.find(t=>t.meta?.missingWater);assert.equal(t.color || t.marker.color,'#e100a8');
  assert.equal(t.intensity,undefined);assert.ok(!t.showscale&&!t.marker?.showscale);
 }
});

test('new display detail, land and missing-material labels render in English',async()=>{
 const e=env(payload),catalog=JSON.parse(fs.readFileSync('3DWET/app/static/i18n/en.json','utf8')),doc=e.context.document;
 const note='静态预览隐藏湖底；半透明蓝色水面与湿网格侧壁展示体积；岸线为代理，未验证；陆地高程未提供';
 const html=fs.readFileSync('3DWET/app/templates/index.html','utf8');
 assert.ok(html.includes(`<p class="sw-legend-note">${note}</p>`),'the legend note must describe the visible water surface and its sampled shoreline');
 assert.equal(catalog.messages[note],'The static preview hides the bed; translucent blue water and wet-grid side walls show the basin volume; the shoreline is a proxy and unverified; land elevation is unavailable.');
 delete e.context.document;
 e.context.fetch=async()=>({ok:true,json:async()=>catalog});
 vm.runInContext(fs.readFileSync('3DWET/app/static/js/i18n.js','utf8'),e.context);
 await e.context.window.StudioI18n.ready;await e.context.window.StudioI18n.setLocale('en-US');e.context.document=doc;
 e.context.fetch=async()=>({json:async()=>payload});await e.context.render3DWaterBody('x',0,{level:0,meshMode:'triangles'});
 assert.doesNotMatch(e.plots[0].layout.title.text,/[\u3400-\u9fff]/);
 for(const trace of e.plots[0].traces)for(const key of ['name','hovertemplate'])if(trace[key])assert.doesNotMatch(trace[key],/[\u3400-\u9fff]/);
});
