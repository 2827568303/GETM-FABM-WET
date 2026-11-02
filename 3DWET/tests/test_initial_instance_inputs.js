const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('3DWET/app/static/js/app.js','utf8');
const elements={'ic-wq-modules':{innerHTML:''},'ic-wq-search':{value:''},'ic-save-status':{}};
let request;
const context=vm.createContext({StudioIcons:{node:()=>({}),svg:()=>'<svg></svg>',setStatus:()=>{}},state:{activeCase:'Isolated lake',icData:{modules:[
  {name:'DOM',category:'有机质',init:{sDW:5}},
  {name:'POM',category:'有机质',init:{sDW:2}},
  {name:'humus',category:'有机质',init:{sDW:.5}}]}},
  $:id=>elements[id],window:{},toast:()=>{},icIcDirty:()=>{},renderIcExtraVars:()=>{},setTimeout:()=>{},
  document:{querySelectorAll:()=>Object.values(elements).filter(e=>e.id?.startsWith('icv-'))},
  api:async(path,options)=>{request=options.body;return {success:true};}});
vm.runInContext(source.slice(source.indexOf('function escapeHtml('),source.indexOf('async function resetParam(')),context);
vm.runInContext(source.slice(source.indexOf('function icPresetVarMap('),source.indexOf('function applyTrophicToFields(')),context);
vm.runInContext(source.slice(source.indexOf('function renderIcWaterQuality('),source.indexOf('// Variables that are not declared')),context);
vm.runInContext(source.slice(source.indexOf('async function saveInitConditions('),source.indexOf('// keep the "elev_const')),context);
context.renderIcWaterQuality();
const inputs=[...elements['ic-wq-modules'].innerHTML.matchAll(/<input[^>]+id="([^"]+)" value="([^"]+)"/g)];
assert.equal(inputs.length,3);
assert.equal(new Set(inputs.map(m=>m[1])).size,3,'shared variable names must not alias different instances');
for(const [,id,value] of inputs)elements[id]={id,value};
elements['icv-POM-sDW'].value='7.25';
(async()=>{await context.saveInitConditions();
  assert.deepEqual(JSON.parse(JSON.stringify(request.water_quality)),{'DOM.sDW':5,'POM.sDW':7.25,'humus.sDW':.5});
  console.log('initial conditions: independent instance inputs and saved values PASS');
})().catch(e=>{console.error(e);process.exitCode=1;});
