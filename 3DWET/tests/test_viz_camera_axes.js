const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {test}=require('node:test');
const source=fs.readFileSync('3DWET/app/static/js/viz3d.js','utf8');
const volume={shape:[2,2,2],xc:[0,100],yc:[0,100],bottom:[[4,8],[4,8]],sigma:[-.75,-.25],
 data:[[[0,1],[0,1]],[[2,3],[2,3]]],min:0,max:3,units:'mg/L'};
function environment(){
 const calls=[],plots=[],listeners={},slider={value:'34',addEventListener(name,fn){listeners[`slider_${name}`]=fn;}},output={textContent:''},positionSlider={value:'0',addEventListener(name,fn){listeners[`position_${name}`]=fn;}},positionOutput={textContent:'0%'},main={innerHTML:'',on:(event,fn)=>{listeners[event]=fn;}},section={innerHTML:''};
 const element=e=>typeof e==='string'?main:e;
 const Plotly={newPlot:async(e,traces,layout)=>{const node=element(e);node._fullLayout={scene:layout.scene};plots.push({node,layout});},
  react:async(e,traces,layout)=>{const node=element(e);node._fullLayout={scene:layout.scene};plots.push({node,layout});},
  relayout:async(e,patch)=>{calls.push(patch);assert.ok(calls.length<20,'camera/axis relayout must not loop');
   const node=element(e);for(const [key,value] of Object.entries(patch)){if(key==='scene.camera')node._fullLayout.scene.camera=value;
    else {const m=key.match(/^scene\.([xyz]axis)\.visible$/);if(m)node._fullLayout.scene[m[1]].visible=value;}}
   listeners.plotly_relayout?.(patch);}};
 const context=vm.createContext({console,URL,URLSearchParams,Plotly,window:{Plotly},document:{getElementById:id=>id==='viz3d-plotly'?main:id==='viz3d-section-plot'?section:id==='viz3d-camera-elevation'?slider:id==='viz3d-camera-elevation-value'?output:id==='viz3d-camera-position'?positionSlider:id==='viz3d-camera-position-value'?positionOutput:null},
  fetch:async()=>({json:async()=>volume})});vm.runInContext(source,context);return {context,main,section,calls,plots,listeners,slider,output,positionSlider,positionOutput};
}
const visible=scene=>[scene.xaxis.visible!==false,scene.yaxis.visible!==false,scene.zaxis.visible!==false];
test('exact named views hide only the collapsed axis and retain visibility after data refresh',async()=>{
 const e=environment();await e.context.render3DCloud('test',0);
 for(const [view,expected] of [['top',[true,true,false]],['front',[true,false,true]],['side',[false,true,true]],['oblique',[true,true,true]],['reset',[true,true,true]]]){
  await e.context.window.set3DCamera(view);assert.deepEqual(visible(e.main._fullLayout.scene),expected,view);
  await e.context.render3DCloud('test',1);assert.deepEqual(visible(e.plots.at(-1).layout.scene),expected,`${view} refresh`);
 }
});
test('rotating away from an exact view restores axes without a relayout loop',async()=>{
 const e=environment();await e.context.render3DCloud('test',0);await e.context.window.set3DCamera('side');
 const camera={eye:{x:2.5,y:.05,z:0},center:{x:0,y:0,z:0},projection:{type:'orthographic'}};
 e.listeners.plotly_relayout({'scene.camera':camera});await new Promise(resolve=>setImmediate(resolve));
 assert.deepEqual(visible(e.main._fullLayout.scene),[true,true,true]);
 await new Promise(resolve=>setImmediate(resolve));
 const afterFirst=e.calls.length;
 const corrected=e.main._fullLayout.scene.camera;
 e.listeners.plotly_relayout({'scene.camera':corrected});await new Promise(resolve=>setImmediate(resolve));
 assert.ok(e.calls.length<=afterFirst+1,'unchanged corrected orientation does not start a relayout loop');
});
test('axis alignment uses eye minus target and leaves independent sections unchanged',async()=>{
 const e=environment();await e.context.render3DCloud('test',0);
 const camera={eye:{x:10,y:20,z:2.5},center:{x:10,y:20,z:0},projection:{type:'orthographic'}};
 e.context.inputCamera=camera;
 assert.deepEqual(JSON.parse(JSON.stringify(vm.runInContext('viz3dCameraAxes(inputCamera)',e.context))),{x:true,y:true,z:false},'panned top direction collapses the depth axis');
 e.listeners.plotly_relayout({'scene.camera':camera});await new Promise(resolve=>setImmediate(resolve));
 assert.deepEqual(visible(e.main._fullLayout.scene),[true,true,false],'the exact top view hides its collapsed depth axis');
 e.context.fetch=async()=>({json:async()=>({data:[[1]],horizontal:[0],horizontal_edges:[-.5,.5],depth_edges:[[4],[0]],min:1,max:1})});
 await e.context.renderSpatialSection('test',0,'xz',0);const scene=e.plots.at(-1).layout.scene;
 assert.deepEqual(visible(scene),[true,false,true]);assert.equal(scene.camera.eye.y,-2);
});

test('a camera moved while the next output frame loads is retained by the actual draw',async()=>{
 const e=environment();await e.context.render3DCloud('test',0);
 const previous=e.main._fullLayout.scene.camera;
 let live=previous,release,started;
 const pending=new Promise(resolve=>{release=resolve;});
 const loading=new Promise(resolve=>{started=resolve;});
 // WebGL exposes the current gesture camera before the final relayout event.
 e.main._fullLayout.scene._scene={getCamera:()=>live};
 e.context.fetch=async()=>{started();await pending;return {json:async()=>volume};};
 const next=e.context.render3DCloud('test',1);await loading;
 live={eye:{x:2.1,y:.4,z:.35},center:{x:.12,y:-.08,z:.03},up:{x:0,y:0,z:1},projection:{type:'orthographic'}};
 release();await next;
 assert.deepEqual(JSON.parse(JSON.stringify(e.plots.at(-1).layout.scene.camera)),live,
  'drawing a fetched frame must retain the camera currently visible, including pan and zoom');
});

test('continuous orbit events retain pan and zoom before the final release event',async()=>{
 const e=environment();await e.context.render3DCloud('test',0);
 const camera={eye:{x:.7,y:-.3,z:.9},center:{x:.25,y:.12,z:-.08},up:{x:0,y:0,z:1},projection:{type:'orthographic'}};
 assert.equal(typeof e.listeners.plotly_relayouting,'function','continuous camera events must be captured');
 e.listeners.plotly_relayouting({'scene.camera':camera});
 await e.context.render3DCloud('test',1);
 assert.deepEqual(JSON.parse(JSON.stringify(e.plots.at(-1).layout.scene.camera)),camera);
});

test('orbiting below the basin remains below the horizontal while preserving pan, zoom, heading and up',async()=>{
 const e=environment();
 const horizontal=Math.hypot(1.2-.2,.7-(-.1));
 const camera={eye:{x:1.2,y:.7,z:.05-horizontal*Math.tan(Math.PI/6)},center:{x:.2,y:-.1,z:.05},up:{x:0,y:0,z:1},projection:{type:'orthographic'}};
 const originalDistance=Math.hypot(camera.eye.x-camera.center.x,camera.eye.y-camera.center.y,camera.eye.z-camera.center.z);
 e.context.inputCamera=camera;
 const corrected=vm.runInContext('viz3dClampCamera(inputCamera)',e.context),dx=corrected.eye.x-corrected.center.x,dy=corrected.eye.y-corrected.center.y,dz=corrected.eye.z-corrected.center.z;
 const distance=Math.hypot(dx,dy,dz),elevation=Math.atan2(dz,Math.hypot(dx,dy));
 assert.ok(Math.abs(elevation+Math.PI/6)<1e-8,'the orbit must retain its 30 degree below-horizontal elevation');
 assert.ok(Math.abs(distance-originalDistance)<1e-8,'clamping must preserve zoom distance');
 assert.ok(Math.abs(Math.atan2(dy,dx)-Math.atan2(camera.eye.y-camera.center.y,camera.eye.x-camera.center.x))<1e-8,'clamping must preserve orbit heading');
 assert.deepEqual(JSON.parse(JSON.stringify(corrected),),camera,'orbit keeps pan, up-vector and projection unchanged');
});

test('orbiting continuously away from top restores the depth axis without waiting for release',async()=>{
 const e=environment();await e.context.render3DCloud('test',0);await e.context.window.set3DCamera('top');
 const camera={eye:{x:1,y:1,z:2},center:{x:0,y:0,z:0},projection:{type:'orthographic'}};
 e.listeners.plotly_relayouting({'scene.camera':camera});await new Promise(resolve=>setImmediate(resolve));
 assert.deepEqual(visible(e.main._fullLayout.scene),[true,true,true]);
});

test('the next draw reads a camera moved while its graph queue is blocked',async()=>{
 const e=environment();await e.context.render3DCloud('test',0);
 let live=e.main._fullLayout.scene.camera,release;
 e.main._fullLayout.scene._scene={getCamera:()=>live};
 e.context.pendingIndicator=new Promise(resolve=>{release=resolve;});
 vm.runInContext('_viz3dIndicatorQueue=pendingIndicator',e.context);
 const next=e.context.render3DCloud('test',1);await new Promise(resolve=>setImmediate(resolve));
 live={eye:{x:3,y:1,z:.2},center:{x:-.2,y:.15,z:.05},projection:{type:'orthographic'}};
 release();await next;
 assert.deepEqual(JSON.parse(JSON.stringify(e.plots.at(-1).layout.scene.camera)),live);
});

test('an old case live camera cannot override the new case default',async()=>{
 const e=environment();await e.context.render3DCloud('test',0,22,{caseKey:'A'});
 e.main._fullLayout.scene._scene={getCamera:()=>({eye:{x:4,y:4,z:4}})};
 await e.context.render3DCloud('test',1,22,{caseKey:'B'});
 assert.equal(e.plots.at(-1).layout.scene.camera.eye.x,0.8525);
});

test('refresh retires the old section indicator without a trace redraw before the new frame',async()=>{
 const e=environment();await e.context.render3DCloud('test',0);
 const camera={eye:{x:.2,y:-.4,z:2.7},center:{x:0,y:0,z:0},projection:{type:'orthographic'}};
 let live=camera,deletions=0;
 e.main.data=[{meta:{section_indicator:true}}];
 e.main._fullLayout.scene._scene={getCamera:()=>live};
 e.context.window.Plotly.deleteTraces=async()=>{deletions++;live={eye:{x:1.55,y:-1.75,z:1.6},projection:{type:'orthographic'}};};
 await e.context.render3DCloud('test',1);
 assert.equal(deletions,0,'the new main draw already removes old indicator traces');
 assert.deepEqual(JSON.parse(JSON.stringify(e.plots.at(-1).layout.scene.camera)),camera);
});

test('playback retains the selected pan, zoom or orbit interaction across data frames',async()=>{
 for(const dragmode of ['pan','zoom','orbit','turntable']) {
  const e=environment();await e.context.render3DCloud('test',0);
  e.main._fullLayout.scene.dragmode=dragmode;
  await e.context.render3DCloud('test',1);
  assert.equal(e.plots.at(-1).layout.scene.dragmode,dragmode);
 }
});
test('orbit can approach either vertical pole while preserving distance, heading, pan and projection',()=>{
 const e=environment();
 for(const sign of [-1,1]) {
  const center={x:.2,y:-.1,z:.05},distance=2.4,azimuth=.7,elevation=sign*(Math.PI/2-.7*Math.PI/180);
  const camera={eye:{x:center.x+distance*Math.cos(elevation)*Math.cos(azimuth),y:center.y+distance*Math.cos(elevation)*Math.sin(azimuth),z:center.z+distance*Math.sin(elevation)},center,up:{x:0,y:0,z:1},projection:{type:'orthographic'}};
  e.context.inputCamera=camera;
  const corrected=vm.runInContext('viz3dClampCamera(inputCamera)',e.context),dx=corrected.eye.x-center.x,dy=corrected.eye.y-center.y,dz=corrected.eye.z-center.z;
  assert.ok(Math.abs(Math.atan2(dz,Math.hypot(dx,dy))-elevation)<1e-8,`${sign} pole elevation remains reachable`);
  assert.ok(Math.abs(Math.hypot(dx,dy,dz)-distance)<1e-8,'zoom distance is preserved');
  assert.ok(Math.abs(Math.atan2(dy,dx)-azimuth)<1e-8,'heading is preserved');
  assert.deepEqual(JSON.parse(JSON.stringify(corrected.center)),center,'pan center is preserved');
  assert.deepEqual(JSON.parse(JSON.stringify(corrected.projection)),camera.projection,'projection is preserved');
 }
});
test('orbit events keep the view free to cross both vertical poles',async()=>{
 const e=environment();await e.context.render3DCloud('test',0);
 const center={x:.1,y:-.2,z:.05},distance=2.4,elevation=Math.PI/2-Math.PI/1800;
 const camera={eye:{x:center.x+distance*Math.cos(elevation),y:center.y,z:center.z+distance*Math.sin(elevation)},center,
  up:{x:0,y:-1,z:0},projection:{type:'orthographic'}};
 e.listeners.plotly_relayouting({'scene.camera':camera});
 await Promise.resolve();
 assert.equal(e.calls.filter(patch=>patch['scene.camera']).length,0,'a continuous gesture must not be corrected at the pole');
 assert.deepEqual(JSON.parse(JSON.stringify(vm.runInContext('_viz3dCamera',e.context))),camera,'the live gesture camera can pass the pole');
 e.listeners.plotly_relayout({'scene.camera':camera});
 await Promise.resolve();
 assert.equal(e.calls.filter(patch=>patch['scene.camera']).length,0,'the final event must not snap the camera back from the flipped orientation');
 assert.deepEqual(JSON.parse(JSON.stringify(vm.runInContext('_viz3dCamera',e.context))),camera,'the flipped camera is retained after release');
});
test('invalid orbit camera events do not replace the last finite non-degenerate camera',async()=>{
 const e=environment();await e.context.render3DCloud('test',0);
 e.listeners.plotly_relayouting({'scene.camera':e.main._fullLayout.scene.camera});
 const original=JSON.parse(JSON.stringify(vm.runInContext('_viz3dCamera',e.context)));
 e.listeners.plotly_relayouting({'scene.camera':{eye:{x:NaN,y:0,z:1},center:{x:0,y:0,z:0},up:{x:0,y:0,z:1}}});
 assert.deepEqual(JSON.parse(JSON.stringify(vm.runInContext('_viz3dCamera',e.context))),original,
  'non-finite camera coordinates cannot poison the camera used by later playback frames');
 e.listeners.plotly_relayouting({'scene.camera':{eye:{x:0,y:0,z:0},center:{x:0,y:0,z:0},up:{x:0,y:0,z:1}}});
 assert.deepEqual(JSON.parse(JSON.stringify(vm.runInContext('_viz3dCamera',e.context))),original,
  'a zero-length camera direction is ignored instead of becoming a singular view');
});
test('the 3D camera defaults to unrestricted orbit mode across frame refreshes',async()=>{
 const e=environment();await e.context.render3DCloud('test',0);
 assert.equal(e.plots.at(-1).layout.scene.dragmode,'orbit','default 3D interaction must allow free orbit pitch');
 await e.context.render3DCloud('test',1);
 assert.equal(e.plots.at(-1).layout.scene.dragmode,'orbit','frame refresh must retain the orbit interaction mode');
});
test('the underside preset points up from below the basin and keeps the vertical axis hidden',async()=>{
 const e=environment();await e.context.render3DCloud('test',0);
 await e.context.window.set3DCamera('bottom');
 assert.equal(e.main._fullLayout.scene.camera.eye.z,-2.5);
 assert.deepEqual(JSON.parse(JSON.stringify(e.main._fullLayout.scene.camera.up)),{x:0,y:1,z:0});
 assert.deepEqual(visible(e.main._fullLayout.scene),[true,true,false]);
});

test('camera elevation conversion preserves azimuth and distance and clamps before vertical singularities',()=>{
 const c=environment().context;
 const original={eye:{x:1.2,y:.7,z:.05},center:{x:.2,y:-.1,z:.05},up:{x:0,y:0,z:1},projection:{type:'orthographic'}};
 const changed=c.viz3dCameraAtElevation(original,30,.7),dx=changed.eye.x-original.center.x,dy=changed.eye.y-original.center.y,dz=changed.eye.z-original.center.z;
 assert.ok(Math.abs(Math.atan2(dz,Math.hypot(dx,dy))-Math.PI/6)<1e-8);
 assert.ok(Math.abs(Math.atan2(dy,dx)-Math.atan2(.8,1))<1e-8);
 assert.ok(Math.abs(Math.hypot(dx,dy,dz)-Math.hypot(1,.8))<1e-8);
 assert.deepEqual(JSON.parse(JSON.stringify(changed.center)),original.center);
 assert.equal(c.viz3dCameraElevationDegrees(changed),30);
 const top=c.viz3dCameraAtElevation(original,120,.7);
 assert.equal(c.viz3dCameraElevationDegrees(top),89,'slider endpoint stays short of the vertical singularity');
});

test('elevation slider changes camera pitch only, syncs presets and follows orbit relayouts',async()=>{
 const e=environment();await e.context.render3DCloud('test',0);
 const original={eye:{x:1.2,y:.7,z:.05},center:{x:.2,y:-.1,z:.05},up:{x:0,y:0,z:1},projection:{type:'orthographic'}};
 e.main._fullLayout.scene.camera=original;e.context.inputCamera=original;
 vm.runInContext('_viz3dCamera=inputCamera',e.context);
 e.main.data=[{meta:{scientificField:true}},{meta:{waterbodyFrame:'bed'}},{meta:{waterbodyFrame:'land'}}];
 await e.context.window.set3DCameraElevation(-30);
 const changed=e.main._fullLayout.scene.camera,dx=changed.eye.x-changed.center.x,dy=changed.eye.y-changed.center.y,dz=changed.eye.z-changed.center.z;
 assert.equal(e.slider.value,'-30');assert.equal(e.output.textContent,'-30°');
 assert.ok(Math.abs(Math.atan2(dz,Math.hypot(dx,dy))+Math.PI/6)<1e-8);
 assert.ok(Math.abs(Math.atan2(dy,dx)-Math.atan2(.8,1))<1e-8);
 assert.ok(Math.abs(Math.hypot(dx,dy,dz)-Math.hypot(1,.8))<1e-8);
 assert.equal(e.main._viz3dUndersideActive,true,'below-water angle activates the existing underside occlusion behavior');
 const manual={...changed,eye:{...changed.eye,x:changed.eye.x+.2,z:changed.eye.z+.3}};
 e.listeners.plotly_relayout({'scene.camera':manual});
 assert.equal(e.slider.value,String(e.context.viz3dCameraElevationDegrees(manual)),'manual orbit updates the control');
 await e.context.window.set3DCamera('bottom');
 assert.equal(e.slider.value,'-89','exact underside preset maps to the nearest nonsingular slider value');
 await e.context.window.set3DCamera('top');
 assert.equal(e.slider.value,'89');
 await e.context.window.set3DCamera('front');
 assert.equal(e.slider.value,'0');
 await e.context.window.set3DCamera('oblique');
 assert.equal(e.slider.value,'34','oblique preset synchronizes to its current positive elevation');
});

test('manual elevation remains active when the next playback frame redraws',async()=>{
 const e=environment();await e.context.render3DCloud('test',0);
 await e.context.window.set3DCameraElevation(22);
 const selected=JSON.parse(JSON.stringify(e.main._fullLayout.scene.camera));
 await e.context.render3DCloud('test',1);
 assert.deepEqual(JSON.parse(JSON.stringify(e.plots.at(-1).layout.scene.camera)),selected);
 assert.equal(e.slider.value,'22');
});

test('vertical position control translates camera and target together without changing view direction',()=>{
 const c=environment().context;
 const original={eye:{x:1.2,y:.7,z:.8},center:{x:.2,y:-.1,z:0},up:{x:0,y:0,z:1},projection:{type:'orthographic'}};
 const moved=c.viz3dCameraAtVerticalPosition(original,35,.45);
 assert.ok(Math.abs(moved.center.z+.1575)<1e-12);
 assert.ok(Math.abs(moved.eye.z-.6425)<1e-12);
 assert.equal(moved.eye.x,original.eye.x);assert.equal(moved.eye.y,original.eye.y);
 assert.equal(moved.center.x,original.center.x);assert.equal(moved.center.y,original.center.y);
 assert.ok(Math.abs(c.viz3dCameraElevationDegrees(moved)-c.viz3dCameraElevationDegrees(original))<=0);
 assert.equal(c.viz3dCameraVerticalPosition(moved,.45),35);
 assert.ok(Math.abs((moved.center.z-original.center.z)+.1575)<1e-12,'35% moves only 35% of the bounded normalized camera travel');
 const extreme=c.viz3dCameraAtVerticalPosition(original,100,.45);
 assert.equal(extreme.center.z,-.45,'full slider travel remains within normalized camera coordinates');
 assert.ok(Math.abs(extreme.eye.z-.35)<1e-12,'eye and target receive the same bounded translation');
});

test('vertical position stays applied through playback, follows manual pan and recenters on reset',async()=>{
 const e=environment();await e.context.render3DCloud('test',0);
 await e.context.window.set3DCameraVerticalPosition(40);
 const moved=JSON.parse(JSON.stringify(e.main._fullLayout.scene.camera));
 assert.equal(e.positionSlider.value,'40');assert.equal(e.positionOutput.textContent,'+40%');
 await e.context.render3DCloud('test',1);
 assert.deepEqual(JSON.parse(JSON.stringify(e.plots.at(-1).layout.scene.camera)),moved);
 const dragged={...moved,center:{...moved.center,z:moved.center.z-.12},eye:{...moved.eye,z:moved.eye.z-.12}};
 e.listeners.plotly_relayout({'scene.camera':dragged});
 const expected=String(vm.runInContext('viz3dCameraVerticalPosition(inputPositionCamera,viz3dVerticalPositionScale(document.getElementById("viz3d-plotly")._fullLayout.scene))',Object.assign(e.context,{inputPositionCamera:dragged})));
 assert.equal(e.positionSlider.value,expected,'manual camera pan updates vertical-position value');
 await e.context.window.set3DCamera('reset');
 assert.equal(e.positionSlider.value,'0','reset view returns model to vertical center');
});

test('the camera control exposes a nonsingular above- and below-water elevation slider',()=>{
 const html=require('node:fs').readFileSync('3DWET/app/templates/index.html','utf8');
 assert.match(html,/<option value="bottom">仰视<\/option>/);
 assert.match(html,/<input id="viz3d-camera-elevation" type="range" min="-89" max="89"/);
 assert.match(html,/<input id="viz3d-camera-position" type="range" min="-100" max="100"/);
 assert.match(html,/0°为水平视线.*正值.*负值/);
 assert.match(html,/垂向放大单独控制/);assert.match(html,/正值让画面中的模型上移.*负值下移.*恢复视图会回中/);
});
