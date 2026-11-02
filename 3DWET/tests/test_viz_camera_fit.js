const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const {test}=require('node:test');
const context=vm.createContext({console,window:{},document:{getElementById:()=>null}});
vm.runInContext(fs.readFileSync('3DWET/app/static/js/viz3d.js','utf8'),context);
test('orthographic lake framing zooms the basin while preserving its proportions and shoreline bounds',()=>{
 const scene=vm.runInContext("lakeScene(2,10,{xc:[100,200,300],yc:[1000,1200]})",context);
 assert.equal(Math.max(...Object.values(scene.aspectratio)),4.5,
  'orthographic zoom must scale all three aspectratio axes because Plotly zooms this projection through aspectratio');
 assert.ok(Math.abs(scene.aspectratio.x/scene.aspectratio.y-300/400)<1e-12,'zoom must preserve physical X/Y proportions');
 assert.ok(Math.abs(scene.aspectratio.z/scene.aspectratio.y-20/400)<1e-12,'zoom must preserve physical Z/Y proportions');
 assert.deepEqual(Array.from(scene.xaxis.range),[50,350],'the visible axis range must retain the complete wet shoreline');
 assert.deepEqual(Array.from(scene.yaxis.range),[900,1300],'the visible axis range must retain the complete wet shoreline');
 assert.ok(Math.abs(Math.atan2(scene.camera.eye.z,Math.hypot(scene.camera.eye.x,scene.camera.eye.y))*180/Math.PI-32.5)<1,
  'the default lake view uses a natural oblique camera while retaining an orthographic projection');
});
test('reset view keeps the selected camera orientation separate from orthographic zoom',async()=>{
 const camera={eye:{x:0,y:0,z:2.5},center:{x:0,y:0,z:0},up:{x:0,y:1,z:0},projection:{type:'orthographic'}};
 context.document.getElementById=()=>({_fullLayout:{},_viz3dAxisVisibility:null});
 context.window.Plotly={relayout:async(_element,patch)=>patch};
 await context.set3DCamera('top');
 assert.deepEqual(JSON.parse(JSON.stringify(vm.runInContext("_viz3dCamera",context))),camera);
});
