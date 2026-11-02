const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const {test}=require('node:test');

const appSource=fs.readFileSync('3DWET/app/static/js/app.js','utf8');
const template=fs.readFileSync('3DWET/app/templates/index.html','utf8');

function loadCompatibility(document){
 const start=appSource.indexOf('function ensureViz3dVolumePresetCompatibility');
 assert.notEqual(start,-1,'app.js should provide a legacy-template volume preset bootstrap');
 const end=appSource.indexOf('\nwindow.addEventListener(\'load\'',start);
 assert.notEqual(end,-1,'compatibility bootstrap should be defined before app load initialization');
 const root={document,window:null};root.window=root;
 vm.runInContext(appSource.slice(start,end),vm.createContext(root));
 return root.ensureViz3dVolumePresetCompatibility;
}

function control(id){
 const attrs={},listeners={};
 return {id,attrs,listeners,children:[],className:'',textContent:'',value:'triangles',checked:false,
  setAttribute(name,value){attrs[name]=value;},append(...items){this.children.push(...items);items.forEach(item=>item.parent=this);},
  appendChild(item){this.append(item);return item;},addEventListener(name,callback){listeners[name]=callback;}};
}

test('compatibility removes a leftover volume preset and triangle option',()=>{
 const mesh=control('viz3d-mesh-mode');
 mesh.value='triangles';
 const triangle=control('option');
 triangle.value='triangles';
 const continuous=control('option');
 continuous.value='continuous';
 mesh.options=[triangle,continuous];
 triangle.remove=()=>{mesh.options=mesh.options.filter(item=>item!==triangle);};
 let presetRemoved=false;
 const preset=control('viz3d-volume-preset');
 preset.remove=()=>{presetRemoved=true;};
 const controls=new Map([
  ['viz3d-mesh-mode',mesh],
  ['viz3d-volume-preset',preset],
 ]);
 const document={
  getElementById(id){return controls.get(id)||null;},
  querySelectorAll(selector){return selector==='#viz3d-mesh-mode option'?mesh.options:[];},
 };
 const ensure=loadCompatibility(document);
 assert.equal(ensure(),false);
 assert.equal(presetRemoved,true);
 assert.equal(mesh.value,'continuous');
 assert.deepEqual(mesh.options.map(item=>item.value),['continuous']);
 assert.equal(ensure(),false);
});

test('current shell has no triangle mesh product entry',()=>{
 assert.doesNotMatch(template,/id="viz3d-volume-preset"/);
 assert.doesNotMatch(template,/viz3d_volume_preset\.js/);
 assert.doesNotMatch(template,/value="triangles"/);
 assert.match(template,/id="run-monitor"/);
 assert.match(template,/不提供三角网或非结构网格/);
});
