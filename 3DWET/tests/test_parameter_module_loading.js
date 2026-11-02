const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const source = fs.readFileSync('3DWET/app/static/js/app.js', 'utf8');
const start = source.indexOf('async function loadParamModules()');
const end = source.indexOf('function loadModuleParams()', start);
const select = {innerHTML:'', options:[], appendChild(option){this.options.push(option);}};
const param = {name:'O2PerNH4W', value:2, type:'number'};
const modules = [{name:'abiotic_water', long_name:'Abiotic water', n_params:1,
  parameters:[param]}];
const state = {activeCasePath:'C:/synthetic/Imported Random Lake', fabmModules:[]};
const requests = [];
const context = vm.createContext({state, $:id=>id==='param-module-select'?select:{},
  document:{createElement:()=>({})}, api:async path=>{requests.push(path);return {modules};},
  loadModuleParams:()=>{}});
vm.runInContext(source.slice(start,end), context);

(async()=>{
  await context.loadParamModules();
  assert.deepEqual(requests, ['/api/config/fabm'],
    'the parameter page should load FABM modules when its in-memory list is empty');
  assert.deepEqual(state.fabmModules.map(m=>m.name), ['abiotic_water']);
  assert.equal(select.options[0].value, 'abiotic_water');
  console.log('parameter module loading: empty state hydrates from active case PASS');
})().catch(error=>{console.error(error);process.exitCode=1;});
