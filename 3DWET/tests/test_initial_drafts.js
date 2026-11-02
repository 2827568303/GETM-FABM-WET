const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('3DWET/app/static/js/app.js','utf8');
let fields=[],requests=[];
const host={_html:'',get innerHTML(){return this._html;},set innerHTML(html){this._html=html;
  fields=[...html.matchAll(/<input[^>]+id="([^"]+)" value="([^"]+)"[^>]*>/g)].map(m=>({id:m[1],value:m[2],dataset:{icPreset:'0',icKey:m[0].match(/data-ic-key="([^"]+)"/)?.[1]}}));}};
const elements={'ic-wq-modules':host,'ic-wq-search':{value:''},'ic-save-status':{}};
const context=vm.createContext({StudioIcons:{node:()=>({}),svg:()=>'<svg></svg>',setStatus:()=>{}},state:{activeCase:'DraftLake',icData:{modules:[
  {name:'DOM',category:'有机质',init:{sDW:5}}, {name:'POM',category:'有机质',init:{sDW:2}}]}},
  $:id=>elements[id]||fields.find(e=>e.id===id),window:{},toast:()=>{},icIcDirty:()=>{},renderIcExtraVars:()=>{},setTimeout:()=>{},
  document:{querySelectorAll:()=>fields},api:async(path,options)=>{requests.push(options.body);return {success:true};}});
vm.runInContext(source.slice(source.indexOf('function escapeHtml('),source.indexOf('async function resetParam(')),context);
vm.runInContext(source.slice(source.indexOf('function icPresetVarMap('),source.indexOf('function applyTrophicToFields(')),context);
vm.runInContext(source.slice(source.indexOf('function renderIcWaterQuality('),source.indexOf('// Variables that are not declared')),context);
vm.runInContext(source.slice(source.indexOf('async function saveInitConditions('),source.indexOf('// keep the "elev_const')),context);
(async()=>{
  context.renderIcWaterQuality();fields.find(e=>e.id==='icv-POM-sDW').value='6.75';
  elements['ic-wq-search'].value='DOM';context.renderIcWaterQuality();
  assert.equal(fields.length,1);
  await context.saveInitConditions();
  assert.equal(requests[0].water_quality['POM.sDW'],6.75,'filtered-out edits must still save');
  elements['ic-wq-search'].value='';context.renderIcWaterQuality();
  assert.equal(fields.find(e=>e.id==='icv-POM-sDW').value,'6.75','saved value must survive another render');
  fields.find(e=>e.id==='icv-POM-sDW').value='';
  await context.saveInitConditions();
  assert.equal(requests.length,1,'empty numeric input must not silently become zero');
  context.state.icData={modules:[{name:'POM',category:'有机质',init:{sDW:9}}]};
  context.renderIcWaterQuality(false);
  assert.match(host.innerHTML,/id="icv-POM-sDW" value="9"/,'fresh load must discard previous case drafts');
  console.log('initial drafts: filter, hidden save, rerender and invalid empty input PASS');
})().catch(e=>{console.error(e);process.exitCode=1;});
