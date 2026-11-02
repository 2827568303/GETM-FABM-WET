const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('3DWET/app/static/js/app.js','utf8');
let response,notifications=[],locale='zh-CN';
const elements=new Map();
const progressBar={setAttribute(){},removeAttribute(){}};
const element=id=>{if(!elements.has(id))elements.set(id,{style:{},parentElement:progressBar,childNodes:[{},{}],replaceChildren(){},appendChild(){},scrollHeight:0,scrollTop:0,clientHeight:0});return elements.get(id);};
const context=vm.createContext({state:{etaNotified:new Set(),lastRunStatus:'running'},api:async()=>response,
  $:element,window:{StudioI18n:{locale:()=>locale,t:(value,params)=>String(value).replace(/\{(\w+)\}/g,(_,key)=>params?.[key]??`{${key}}`)}},document:{querySelector:element,createElement:()=>({})},setInterval:()=>1,clearInterval(){},
  fmt:(v,d)=>Number(v).toFixed(d),syncQgisStatusBar(){},ModelDates:{formatText:t=>t},renderFabmRepairSummary(){},advanceOutputRevision(){},updateRunNotificationStatus(){},runFailureReason:s=>s.logs?.find(line=>line.includes('[ERROR]'))||'no reason',notifyUser:(title,body)=>notifications.push({title,body}),
  loadVariables(){},loadDashboardSummary(){}});
vm.runInContext(source.slice(source.indexOf('function runStepSummary('),source.indexOf('function updateRunNotificationStatus(')),context);
vm.runInContext(source.slice(source.indexOf('function appendRunLogLines('),source.indexOf('async function loadMpiRunCapabilities(')),context);
vm.runInContext(source.slice(source.indexOf('async function pollRunStatus('),source.indexOf('// ── Variables')),context);
async function poll(eta,status='running',logs=[]) {
  response={status,eta_minutes:eta,progress:50,elapsed:10,current_step:5,total_steps:10,steps_per_second:8.4,performance:{solver_mode:'预编译串行求解器'},logs};
  await context.pollRunStatus();
}
(async()=>{
  await poll(4);assert.equal(notifications.length,0,'first short ETA must not pretend to cross all three thresholds');
  assert.match(element('run-step-info').textContent,/步数: 5 \/ 10 · 8\.4 步\/秒 · 预编译串行求解器/,'Chinese step summary remains unchanged');
  await poll(65);await poll(59);assert.equal(notifications.length,1);assert.match(notifications[0].body,/60分钟阈值/);
  await poll(16);await poll(14);assert.equal(notifications.length,2);
  await poll(NaN);await poll(5);assert.equal(notifications.length,3,'invalid ETA must not erase the last valid baseline');
  await poll(10);await poll(4);assert.equal(notifications.length,3,'each threshold fires once per run');
  await poll(0,'completed');await poll(0,'completed');assert.equal(notifications.length,4,'completion fires once');
  context.state.lastRunStatus='running';await poll(0,'failed',['[ERROR] isolated solver failure reason']);await poll(0,'failed');assert.equal(notifications.length,5,'failure fires once');
  assert.match(notifications.at(-1).body,/isolated solver failure reason/,'failure notification should surface the available log reason');
  locale='en-US';context.state.lastRunStatus='running';await poll(0,'completed');
  assert.equal(element('run-step-info').textContent,'Steps: 5 / 10 · 8.4 steps/s · Precompiled serial solver');
  assert.equal(element('#run-status-display').childNodes[1].textContent,'Completed');
  assert.equal(notifications.at(-1).title,'Model run completed');
  assert.equal(notifications.at(-1).body,'5 steps · total task time 0.2 min, including post-processing');
  context.state.lastRunStatus='running';await poll(0,'failed',['[ERROR] isolated solver failure reason']);
  assert.equal(notifications.at(-1).title,'Model run failed');
  assert.equal(notifications.at(-1).body,'Failure reason: [ERROR] isolated solver failure reason');
  context.state.lastRunStatus='running';await poll(0,'stopped');
  assert.equal(notifications.at(-1).title,'Model run stopped');
  assert.equal(notifications.at(-1).body,'Stopped at step 5');
  console.log('run notifications: true ETA crossings, invalid estimates, deduplication and terminal states PASS');
})().catch(e=>{console.error(e);process.exitCode=1;});
