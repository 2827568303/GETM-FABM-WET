const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('3DWET/app/static/js/app.js','utf8');
const container={innerHTML:'',classList:{add(){},remove(){}}};
const canvas={};
const state={activeCasePath:'C:/cases/static',caseRevision:3};
const geometry={depth:[[3,2],[0,1]],wetMask:[[true,true],[false,true]],dry_mask:[[false,false],[true,false]],
  xc:[0,10],yc:[0,10],coordinate_mode:'projected',authoritative_boundary:{projected_polygons:[{outer:[[0,0]]}]}};
let drawArgs=null;
const context=vm.createContext({state,window:{StudioI18n:{scientificText:(zh,en)=>en},ScientificHeatmap:{
  validateBoundary:(boundary,args)=>boundary?.projected_polygons?.length&&args.wetMask?{source:'uploaded-boundary-shapefile'}:null,
  draw:(_canvas,data,args)=>{drawArgs={data,args};}
}},
  $:id=>id==='dashboard-mini-heatmaps'?container:id==='dashboard-static-bathymetry'?canvas:null,
  getScientificGeometry:async()=>geometry,escapeHtml:String,escapeAttr:String});
context.$=id=>id==='dashboard-vars'?{innerHTML:''}:id==='dashboard-mini-heatmaps'?container:id==='dashboard-static-bathymetry'?canvas:null;
context.api=async()=>({error:'没有输出文件'});
context.fmt=String;context.resultLabel=(_,key)=>key;
const summaryStart=source.indexOf('async function loadDashboardSummary()');
const summaryEnd=source.indexOf('async function loadDashboardStaticPreview()',summaryStart);
vm.runInContext(source.slice(summaryStart,summaryEnd),context);
const start=source.indexOf('async function loadDashboardStaticPreview()');
const end=source.indexOf('async function loadDashboardMiniHeatmaps()',start);
vm.runInContext(source.slice(start,end),context);
(async()=>{
  await context.loadDashboardSummary();
  assert.match(container.innerHTML,/data-preview-state="static"/,'a missing-output summary error must switch the home canvas to static bathymetry');
  await context.loadDashboardStaticPreview();
  assert.match(container.innerHTML,/data-preview-state="static"/,'a case with bathymetry and no output gets a home-page static preview');
  assert.match(container.innerHTML,/Static depth preview · model not run/,'the preview is explicitly marked static and not run');
  assert.match(container.innerHTML,/Display outline: uploaded-boundary-shapefile agrees with the wet\/dry mask \(display clipping only; geographic\/scientific validity unverified\)/,
    'accepted source-boundary provenance is visible, while the validation scope stays limited to display clipping');
  assert.deepEqual(JSON.parse(JSON.stringify(drawArgs.data)),[[3,2],[null,1]],'only wet bathymetry cells are displayed');
  assert.equal(drawArgs.args.boundary,geometry.authoritative_boundary,'the validated source outline is passed to the display clip');
  geometry.authoritative_boundary=null;
  await context.loadDashboardStaticPreview();
  assert.match(container.innerHTML,/data-boundary-source="wet-mask-proxy"/,'missing outline explicitly uses wet-grid proxy provenance');
  assert.match(container.innerHTML,/wet-cell edge proxy; no valid saved boundary/,'fallback is labeled and does not claim a geographic shoreline');
  console.log('dashboard static bathymetry preview and outline provenance PASS');
})().catch(error=>{console.error(error);process.exitCode=1;});
