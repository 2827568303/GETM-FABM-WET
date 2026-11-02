const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('3DWET/app/static/js/app.js','utf8');
const state={activeCasePath:null,caseRevision:0};
const elements={'case-badge':{style:{},textContent:''},'footer-status':{textContent:''}};
const calls=[];
const data={case_name:'Lake A',case_path:'C:/cases/a',case_generation:7,case_type:'getm',read_only:false,
  run_info:{nlev:10},fabm:{total_modules:4,modules:[]},has_results:true,output_ntimesteps:24};
const context=vm.createContext({state,document:{body:{classList:{toggle(){}}}},window:{ObservationManager:{setColumnVariableInventory(){} }},
  $:id=>elements[id],api:async url=>{calls.push(url);return url==='/api/case/current'?data:{nwater:123};},
  syncQgisStatusBar(){},refreshCaseStatistics: value=>calls.push(['stats',value]),
  renderProxyCaseStatus: value=>calls.push(['proxy',value]),
  loadDashboardSummary:()=>calls.push('dashboard'),loadVariables:()=>calls.push('variables')});
const start=source.indexOf('async function restoreCurrentCase()');
const end=source.indexOf('async function loadVariables()',start);
vm.runInContext(source.slice(start,end),context);
(async()=>{
  assert.equal(await context.restoreCurrentCase(),true);
  assert.ok(calls.some(call=>Array.isArray(call)&&call[0]==='stats'),
    'restoring a persisted active case must initialize its case statistics');
  assert.ok(calls.includes('dashboard'),
    'restoring a case with output must populate the dashboard summary and mini heatmaps');
  console.log('restored-case dashboard initialization PASS');
})().catch(error=>{console.error(error);process.exitCode=1;});
