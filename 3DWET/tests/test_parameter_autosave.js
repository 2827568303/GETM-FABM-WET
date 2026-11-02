const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('3DWET/app/static/js/app.js', 'utf8');
const sent = [];
const timers = [];
const param = {name:'O2PerNH4W', value:2, saved_value:2, type:'number'};
const elements = {'param-module-select':{value:'abiotic_water'}, 'params-list':{innerHTML:'', rows:[], appendChild(row){this.rows.push(row);}}, 'param-saved-0':{}};
const context = vm.createContext({StudioIcons:{node:()=>({}),svg:()=>'<svg></svg>',setStatus:()=>{}},
  state:{fabmModules:[{name:'abiotic_water', parameters:[param]}], currentParams:[param]},
  $:id=>elements[id] || {}, document:{createElement:()=>({})}, window:{},
  api:async(url, options)=>{sent.push({url, body:options.body}); return {success:true};},
  setTimeout:fn=>{timers.push(fn); return timers.length;}, clearTimeout:()=>{}, toast:()=>{}
});
vm.runInContext(source.slice(source.indexOf('function renderParams('), source.indexOf('// ── Time Settings')), context);

(async()=>{
  context.renderParams([param]);
  const row = elements['params-list'].rows[0];
  assert.match(row.innerHTML, /oninput="[^"]*scheduleParamSave\(this, 'abiotic_water', 'O2PerNH4W'\)/,
    'typing should queue an autosave');
  const input = {value:'2.002', dataset:{idx:'0',type:'number'}, classList:{remove(){}}};
  context.scheduleParamSave(input, 'abiotic_water', 'O2PerNH4W');
  assert.equal(timers.length, 1, 'input edit should schedule a save');
  await timers[0]();
  assert.equal(sent.length, 1);
  assert.equal(sent[0].url, '/api/config/fabm/param');
  assert.equal(sent[0].body.module, 'abiotic_water');
  assert.equal(sent[0].body.param, 'O2PerNH4W');
  assert.equal(sent[0].body.value, 2.002);
  assert.equal(param.saved_value, 2.002, 'successful autosave should update the saved baseline');
  console.log('parameter autosave: input schedules persisted update and clears dirty baseline PASS');
})().catch(error=>{console.error(error); process.exitCode=1;});

