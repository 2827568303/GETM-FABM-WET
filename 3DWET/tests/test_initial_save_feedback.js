const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const source=fs.readFileSync('3DWET/app/static/js/app.js','utf8');

const elements={
  'ic-elev':{value:'0'},
  'ic-temp':{value:'15'},
  'ic-surface-abs':{value:''},
  'ic-datum-abs':{value:''},
  'ic-macro-sd':{value:''},
  'ic-save-status':{textContent:''},
};
const toasts=[];
const context=vm.createContext({StudioIcons:{node:()=>({}),svg:()=>'<svg></svg>',setStatus:(el,_icon,label)=>{if(el)el.textContent=label;}},
  state:{activeCase:'Synthetic save-feedback case',icData:{dirty:true,draftInputs:{},modules:[],trophic:null}},
  $:id=>elements[id]||null,
  api:async()=>({success:true,n_written:0,notes:['getm.inp 已写入'],warnings:['写入 fabm.yaml 失败: synthetic permission error']}),
  toast:(message,type)=>toasts.push({message,type}),
  captureIcDrafts:()=>{},
  Object,
  Number,
  String,
  setTimeout:()=>0,
});
vm.runInContext(source.slice(source.indexOf('async function saveInitConditions('),source.indexOf('// keep the "elev_const')),context);

(async()=>{
  await context.saveInitConditions();
  assert.equal(elements['ic-save-status'].textContent,
    '部分保存失败：写入 fabm.yaml 失败: synthetic permission error',
    'partial persistence warnings must be visible in the save status');
  assert.equal(context.state.icData.dirty,true,'partial save must remain marked dirty');
  assert.ok(toasts.some(item=>item.type==='warning'&&item.message.includes('部分保存失败')),
    'partial persistence must not be announced as a success');
  assert.ok(!toasts.some(item=>item.type==='success'&&item.message.includes('已保存')),
    'partial persistence must not emit the normal success toast');
  console.log('initial condition save feedback: partial-write warnings remain visible');
})().catch(error=>{console.error(error);process.exitCode=1;});
