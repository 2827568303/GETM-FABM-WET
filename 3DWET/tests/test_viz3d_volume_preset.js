const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const {test}=require('node:test');

const modulePath='3DWET/app/static/js/viz3d_volume_preset.js';

function makeControl(value,checked=false){
 const listeners={};
 return {value,checked,listeners,attrs:{},classList:{toggle(){}},
  addEventListener(name,callback){listeners[name]=callback;},
  setAttribute(name,next){this.attrs[name]=next;}};
}

function loadPreset(meshMode='orthogonal',stacked=false,layer='3'){
 if(!fs.existsSync(modulePath))assert.fail('volume preset module should provide a reversible one-step view preset');
 const controls={
  'viz3d-volume-preset':makeControl(''),
  'viz3d-mesh-mode':makeControl(meshMode),
  'viz3d-iso-stack':makeControl('',stacked),
  'viz3d-iso-layer':makeControl(layer),
 };
 const saves=[],root={document:{readyState:'complete',getElementById:id=>controls[id]},
  Viz3dMeshModePreference:{save:value=>{saves.push(value);return true;}},
  updateViz3dIso(){this.renderCount=(this.renderCount||0)+1;},renderCount:0};
 const context=vm.createContext({window:root});
 vm.runInContext(fs.readFileSync(modulePath,'utf8'),context);
 return {preset:root.Viz3dVolumePreset,controls,saves,root};
}

test('volume preset enables triangle mesh and layers together, then restores the prior selections',()=>{
 const {preset,controls,saves,root}=loadPreset('orthogonal',false);
 assert.equal(preset.bind(),true);
 controls['viz3d-volume-preset'].listeners.click();
 assert.equal(controls['viz3d-mesh-mode'].value,'triangles');
 assert.equal(controls['viz3d-iso-stack'].checked,true);
 assert.equal(controls['viz3d-iso-layer'].value,'-1','the preset includes all available layers, not only the current slice');
 assert.equal(controls['viz3d-volume-preset'].attrs['aria-pressed'],'true');
 controls['viz3d-volume-preset'].listeners.click();
 assert.equal(controls['viz3d-mesh-mode'].value,'orthogonal');
 assert.equal(controls['viz3d-iso-stack'].checked,false);
 assert.equal(controls['viz3d-iso-layer'].value,'3');
 assert.equal(controls['viz3d-volume-preset'].attrs['aria-pressed'],'false');
 assert.deepEqual(saves,['triangles','orthogonal']);
 assert.equal(root.renderCount,2,'each preset transition redraws once');
});

test('volume preset preserves a previously selected mesh and stacked-layer state',()=>{
 const {preset,controls}=loadPreset('hidden',true,'5');
 preset.bind();controls['viz3d-volume-preset'].listeners.click();
 controls['viz3d-volume-preset'].listeners.click();
 assert.equal(controls['viz3d-mesh-mode'].value,'hidden');
 assert.equal(controls['viz3d-iso-stack'].checked,true);
 assert.equal(controls['viz3d-iso-layer'].value,'5');
});

test('manual mesh or stack edits exit the preset without discarding the user choice',()=>{
 const {preset,controls}=loadPreset('continuous',false);
 preset.bind();controls['viz3d-volume-preset'].listeners.click();
 controls['viz3d-mesh-mode'].value='orthogonal';
 controls['viz3d-mesh-mode'].listeners.change();
 assert.equal(controls['viz3d-volume-preset'].attrs['aria-pressed'],'false');
 controls['viz3d-volume-preset'].listeners.click();
 controls['viz3d-volume-preset'].listeners.click();
 assert.equal(controls['viz3d-mesh-mode'].value,'orthogonal');
 assert.equal(controls['viz3d-iso-stack'].checked,true);
});

test('template no longer exposes the triangle volume preset',()=>{
 const html=fs.readFileSync('3DWET/app/templates/index.html','utf8');
 assert.doesNotMatch(html,/id="viz3d-volume-preset"/);
 assert.doesNotMatch(html,/viz3d_volume_preset\.js/);
 assert.doesNotMatch(html,/value="triangles"/);
 assert.match(html,/不提供三角网或非结构网格/);
});
