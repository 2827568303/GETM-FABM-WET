const assert=require('node:assert/strict'), fs=require('node:fs'), vm=require('node:vm');
const source=fs.readFileSync('3DWET/app/static/js/app.js','utf8');
let fields=[], requests=[],messages=[];
function parse(html){return [...html.matchAll(/<input\b[^>]*>/g)].map(([tag])=>{
 const attr=name=>tag.match(new RegExp(name+'="([^"]*)"'))?.[1];
 const value=attr('value')||'';
 return {id:attr('id'),value:Number.isFinite(Number(value))?value:'',dataset:{icKey:attr('data-ic-key'),icPreset:attr('data-ic-preset'),icUser:attr('data-ic-user')}};
});}
const host={set innerHTML(html){this.html=html;fields=parse(html);},get innerHTML(){return this.html;},appendChild(div){this.html+=div.innerHTML;fields.push(...parse(div.innerHTML));}};
const elements={'ic-wq-modules':host,'ic-wq-search':{value:''},'ic-save-status':{}};
const modules=[{name:'abiotic_water',category:'water',init:{sO2W:9,sNO3W:1}},
 {name:'DOM',category:'organic',init:{sDW:10}}, {name:'POM',category:'organic',init:{sDW:5}},
 {name:'humus',category:'organic',init:{sDW:12}},
 {name:'diatoms',category:'algae',init:{sDW:.3}}, {name:'zoobenthos',category:'benthos',init:{sD:.4}}];
const presets={eutrophic:{label:'富营养（藻类浊水态）',sO2W:10,sNO3W:1,DOM_sDW:10,POM_sDW:5,diatoms_sDW:.3,zoobenthos_sD:.4,macro_sD:8},
 mesotrophic:{label:'中营养（水草清水态）',sO2W:8,sNO3W:.3,DOM_sDW:5,POM_sDW:2,diatoms_sDW:.1,zoobenthos_sD:.25,macro_sD:15}};
const find=id=>elements[id]||fields.find(f=>f.id===id);
const context=vm.createContext({StudioIcons:{node:()=>({}),svg:()=>'<svg></svg>',setStatus:()=>{}},state:{activeCase:'PresetLake',icData:{modules,trophic:'eutrophic',preset_values:presets,trophic_presets:{eutrophic:'富营养',mesotrophic:'中营养'}}},
 $:find,window:{},toast:(msg)=>messages.push(msg),icIcDirty:()=>{},renderTrophicPicker:()=>{},setTimeout:()=>{},
 document:{querySelectorAll:()=>fields,getElementById:id=>find(id)||null,createElement:()=>({})},
 api:async(path,opts)=>{requests.push(opts.body);return {success:true};}});
vm.runInContext(source.slice(source.indexOf('function escapeHtml('),source.indexOf('async function resetParam(')),context);
vm.runInContext(source.slice(source.indexOf('function icPresetVarMap('),source.indexOf('// keep the "elev_const')),context);
(async()=>{
 context.renderIcWaterQuality();
 assert.ok(!fields.some(f=>f.dataset.icKey==='label'),'preset label must never become a numeric water-quality field');
 assert.ok(!fields.some(f=>f.id.startsWith('icv-new-')),'declared module aliases must not produce duplicate inputs');
 find('icv-POM-sDW').value='7.25';context.onIcVarEdit(find('icv-POM-sDW'));
 await context.saveInitConditions();
 assert.equal(requests.length,1,'complete preset must allow saving');
 assert.equal(requests[0].water_quality['POM.sDW'],7.25);
 assert.equal(requests[0].water_quality['DOM.sDW'],10);
 assert.ok(!Object.hasOwn(requests[0].water_quality,'label'));
 context.state.icData.trophic='mesotrophic';context.applyTrophicToFields();
 assert.equal(Number(find('icv-POM-sDW').value),2,'explicit refill must target POM, not first sDW instance');
 assert.equal(Number(find('icv-DOM-sDW').value),5);
 assert.equal(Number(find('icv-humus-sDW').value),12,'ambiguous bare names must not overwrite another instance');
 assert.equal(Number(find('icv-abiotic_water-sO2W').value),8);
 find('icv-POM-sDW').value='7.25';context.onIcVarEdit(find('icv-POM-sDW'));
 find('icv-DOM-sDW').value='6.125';context.onIcVarEdit(find('icv-DOM-sDW'));
 context.state.icData.trophic='eutrophic';context.applyPresetToFields();
 assert.equal(Number(find('icv-DOM-sDW').value),6.125,'selective preset must preserve user edits');
 assert.equal(Number(find('icv-POM-sDW').value),7.25,'selective preset must preserve manually edited POM');
 assert.equal(Number(find('icv-abiotic_water-sO2W').value),10,'untouched preset inputs should update');
 context.renderIcWaterQuality();
 assert.equal(Number(find('icv-DOM-sDW').value),6.125,'rerender must retain user draft');
 console.log('Initial full presets: metadata excluded, aliases unique, refill targeted, user drafts preserved PASS');
})().catch(e=>{console.error(e);process.exitCode=1;});
