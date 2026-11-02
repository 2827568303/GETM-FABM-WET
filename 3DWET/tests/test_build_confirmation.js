const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('3DWET/app/static/js/app.js','utf8');
let decision;const requests=[];
const context=vm.createContext({StudioIcons:{node:()=>({}),svg:()=>'<svg></svg>',setStatus:()=>{}},state:{activeCase:'New Lake',engines:[],icData:{}},window:{},
 $:id=>({value:id==='build-dt'?'2':'6'}),
 _readModelPeriod:()=>({start:'2020-01-01 00:00:00',stop:'2020-01-01 00:20:00'}),
 confirm:()=>false,confirmStudio:()=>new Promise(resolve=>{decision=resolve;}),
 api:async(url)=>{requests.push(url);return {files:[],fabm:{modules:[],categories:{}}};},
 _ppStatus(){},toast(){},loadInputData(){},loadCases(){},renderModuleCards(){},loadParamModules(){}});
vm.runInContext(source.slice(source.indexOf('function refreshCaseStatistics('),source.indexOf('function applyLoadedCase(')),context);
vm.runInContext(source.slice(source.indexOf('async function buildCase()'),source.indexOf('// ── Modules ─')),context);
(async()=>{
 let running=context.buildCase();
 assert.equal(typeof decision,'function','build must await the in-app confirmation');
 assert.equal(requests.length,0,'no file mutation before confirmation');
 decision(false);await running;assert.equal(requests.length,0,'cancel must keep files untouched');
 running=context.buildCase();decision(true);await running;
 assert.equal(requests.filter(p=>p==='/api/case/build').length,1,'confirmation starts exactly one build');
 console.log('Build confirmation: waits, cancellation leaves inputs intact, acceptance starts once PASS');
})().catch(error=>{console.error(error);process.exitCode=1;});
