const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {test}=require('node:test');
const volume={shape:[2,2,2],xc:[0,100],yc:[0,100],bottom:[[4,8],[4,8]],sigma:[-.75,-.25],
 data:[[[0,1],[0,1]],[[2,3],[2,3]]],min:0,max:3,units:'mg/L',long_name:'temperature'};
function environment(data=volume){const plots=[],updates=[],node={innerHTML:'',clientWidth:390,clientHeight:430},status={textContent:''};
 const Plotly={newPlot:async(e,traces,layout,config)=>{node._fullLayout={scene:layout.scene};plots.push({traces,layout,config});},relayout:async(e,patch)=>updates.push(patch)};
 const context=vm.createContext({console,Plotly,URL,URLSearchParams,window:{Plotly},document:{getElementById:id=>id==='viz3d-plotly'?node:id==='viz3d-status'?status:null},
  fetch:async url=>({json:async()=>String(url).includes('/api/geo/grid?display=scientific')?{shape:[data.data.length,data.data[0].length],coordinate_mode:'index',coordinate_units:'index',wetMask:data.data.map(row=>row.map(()=>true))}:data})});vm.runInContext(fs.readFileSync('3DWET/app/static/js/viz3d.js','utf8'),context);return {context,node,status,plots,updates};}
test('portrait plots compact long metadata titles while every mode retains actual time in status',async()=>{
 for(const mode of ['water','cloud','iso','height']){const e=environment(mode==='height'?{...volume,data:volume.data[0]}:volume),opts={timeLabel:'2026-DOY288 12:34:56',ve:1};
  if(mode==='water')await e.context.render3DWaterBody('test',0,opts);
  else if(mode==='cloud')await e.context.render3DCloud('test',0,22,opts);
  else if(mode==='iso')await e.context.render3DSurface('test',0,18,opts);
  else await e.context.render2DAs3DSurface('test',0,0,opts);
  assert.equal(e.plots[0].layout.title.text.split('<br>').length,1,mode);assert.equal(e.plots[0].layout.showlegend,false,mode);
  assert.equal(e.plots[0].config.displayModeBar,true,`${mode} tools stay visible instead of an empty hover-only frame`);
  assert.ok(e.plots[0].traces.some(t=>t.showscale===true || t.marker?.showscale===true),`${mode} retains an exportable quantitative colourbar`);
  assert.match(e.status.textContent,/2026-DOY288 12:34:56/,`${mode} date stays outside compact plot`);
 }
});
test('desktop to portrait resize compacts metadata without losing it or changing the camera',async()=>{
 const e=environment();e.node.clientWidth=900;e.node.clientHeight=500;
 await e.context.render3DWaterBody('test',0,{ve:1,timeLabel:'2026-DOY288 12:34:56'});assert.ok(e.plots[0].layout.title.text.includes('<br>'));
 e.node.clientWidth=390;e.node.clientHeight=430;await e.context.window.resizeScientific3D(e.node);
 assert.equal(e.updates[0].title.text.split('<br>').length,1);assert.equal(e.updates[0].showlegend,false);assert.equal(e.updates[0].width,390);
 assert.ok(!Object.keys(e.updates[0]).some(k=>k.includes('camera')));assert.match(e.status.textContent,/2026-DOY288 12:34:56/);
 e.node.clientWidth=900;await e.context.window.resizeScientific3D(e.node);
 assert.ok(e.updates[1].title.text.includes('<br>'));assert.equal(e.updates[1].showlegend,true);
});
test('portrait scene keeps the source XYZ scale instead of shrinking the Plotly scene',async()=>{
 const e=environment();e.node.clientWidth=360;e.node.clientHeight=370;
 await e.context.render3DWaterBody('test',0,{ve:1});const first=e.plots[0].layout;
 const source=e.node._viz3dResponsiveSource.layout,original=source.scene.aspectratio,fitted=first.scene.aspectratio;
 const fit=Math.min(1,.75*(360-first.margin.l-first.margin.r)/(370-first.margin.t-first.margin.b));
 assert.ok(fit<1,'this viewport triggers the old shrinking path');
 assert.deepEqual(fitted,original,'narrow layout must preserve Plotly aspectratio scale so it does not zoom the scene out');
 assert.equal(Math.max(...Object.values(original)),4.5,'lakeScene applies a shared orthographic zoom while preserving normalized XYZ proportions');
 assert.ok(Math.abs(fitted.x/fitted.y-original.x/original.y)<1e-12);assert.ok(Math.abs(fitted.z/fitted.x-original.z/original.x)<1e-12);
 await e.context.window.resizeScientific3D(e.node);await e.context.window.resizeScientific3D(e.node);
 assert.deepEqual(e.updates[0]['scene.aspectratio'],fitted);assert.deepEqual(e.updates[1]['scene.aspectratio'],fitted,'repeated resize must not shrink again');
 e.node.clientWidth=900;e.node.clientHeight=500;await e.context.window.resizeScientific3D(e.node);
 assert.deepEqual(e.updates[2]['scene.aspectratio'],original,'desktop restores the original scene dimensions');
 assert.ok(!Object.keys(e.updates[2]).some(k=>k.includes('camera')));
});
test('portrait title sits below the controls row and scene margins reserve space for axis labels',async()=>{
 const e=environment();e.node.clientWidth=360;e.node.clientHeight=370;await e.context.render3DWaterBody('test',0,{ve:1});
 const layout=e.plots[0].layout;assert.equal(layout.title.yref,'container');assert.equal(layout.title.yanchor,'top');
 const titleTop=e.node.clientHeight*(1-layout.title.y);assert.ok(titleTop>=36&&titleTop<50,'title follows the roughly 32px controls row');
 assert.ok(layout.margin.t>=56);assert.ok(layout.margin.l>=30);assert.ok(layout.margin.r>=110);assert.ok(layout.margin.b>=24);
});
