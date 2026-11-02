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

test('old rendered shell receives a reversible volume preset from the current app.js asset',()=>{
 const display=control('sw-3d-display-controls');
 const controls=new Map([
  ['viz3d-mesh-mode',control('viz3d-mesh-mode')],
  ['viz3d-iso-stack',control('viz3d-iso-stack')],
  ['viz3d-iso-layer',control('viz3d-iso-layer')],
  ['viz3d-volume-preset',null],
 ]);
 // The deployed old template has the legacy control row but no preset button/script.
 const oldMarkup=template.replace(/<button[^>]*id="viz3d-volume-preset"[\s\S]*?<\/button>/,'')
  .replace(/<script src="\/static\/js\/viz3d_volume_preset\.js\?v=1"><\/script>/,'');
 assert.doesNotMatch(oldMarkup,/id="viz3d-volume-preset"|viz3d_volume_preset\.js/);
 const scripts=[];
 const created=[];
 const document={
  getElementById(id){return id==='sw-3d-display-controls'?display:controls.get(id)||created.find(item=>item.id===id)||null;},
  createElement(tag){const item=control(tag);created.push(item);return item;},
  querySelector(selector){
   if(selector==='.sw-3d-display-controls')return display;
   return selector==='script[data-viz3d-volume-preset-compat]'?scripts[0]||null:null;
  },
  head:{appendChild(script){scripts.push(script);script.onload?.();}},
 };
 const ensure=loadCompatibility(document);
 assert.equal(ensure(),true);
 const button=document.getElementById('viz3d-volume-preset');
 assert.ok(button,'legacy page should receive the preset control');
 assert.equal(button.textContent,'体网格预设');
 assert.equal(button.attrs['aria-pressed'],'false');
 assert.equal(button.attrs['data-i18n'],'体网格预设');
 assert.equal(display.children.includes(button),true,'button should appear beside the 3D display controls');
 assert.equal(scripts.length,1);
 assert.equal(scripts[0].src,'/static/js/viz3d_volume_preset.js?v=1');
 assert.equal(ensure(),true);
 assert.equal(scripts.length,1,'repeated bootstrap should not insert duplicate modules');
});

test('current shell keeps its native preset markup and script path',()=>{
 assert.match(template,/id="viz3d-volume-preset"/);
 assert.match(template,/viz3d_volume_preset\.js\?v=1/);
});
