const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('3DWET/app/static/js/app.js','utf8');
const pending=[];const elements={'dashboard-vars':{innerHTML:''},'dashboard-mini-heatmaps':{innerHTML:'',classList:{remove(){}}}};
const state={activeCase:'Case A',activeCasePath:'C:/cases/a',caseRevision:1};
const context=vm.createContext({state,$:id=>elements[id],api:url=>new Promise(resolve=>pending.push({url,resolve})),
  fmt:(value)=>String(value),resultLabel:(_,key)=>key,escapeHtml:value=>String(value),escapeAttr:value=>String(value),
  document:{createElement:tag=>({tagName:tag,value:'',textContent:''})},
  window:{StudioI18n:{scientificText:(_source,english)=>english}},drawHeatmap(){}});
const start=source.indexOf('async function loadDashboardSummary(');
vm.runInContext(source.slice(source.indexOf('function resultVariablePriority('), source.indexOf('function prioritizeResultVariables(')), context);
vm.runInContext(source.slice(start,source.indexOf('// ── 2D Visualization',start)),context);
function summary(name,mean){return {[name]:{mean,min:mean-1,max:mean+1,units:'C'}};}
function heatmap(name,mean){return {[name]:{mean,min:mean-1,max:mean+1,units:'g/m3',data:[[mean]]}};}
(async()=>{
  const oldRequest=context.loadDashboardSummary();
  state.activeCase='Case B';state.activeCasePath='C:/cases/b';state.caseRevision++;
  const newRequest=context.loadDashboardSummary();
  pending[1].resolve(summary('case_b_temp',20));await newRequest;
  pending[2].resolve(heatmap('case_b_surface',20));
  pending[0].resolve(summary('case_a_temp',10));await oldRequest;
  await new Promise(resolve=>setImmediate(resolve));
  assert.match(elements['dashboard-vars'].innerHTML,/case_b_temp/);
  assert.doesNotMatch(elements['dashboard-vars'].innerHTML,/case_a_temp/,
    'a late dashboard response from the previous case must not overwrite the active case');
  assert.match(elements['dashboard-mini-heatmaps'].innerHTML,/case_b_surface/);
  const oldHeatmap=context.loadDashboardMiniHeatmaps();
  state.activeCase='Case C';state.activeCasePath='C:/cases/c';state.caseRevision++;
  const newHeatmap=context.loadDashboardMiniHeatmaps();
  pending[4].resolve(heatmap('case_c_surface',30));await newHeatmap;
  pending[3].resolve(heatmap('case_b_surface',20));await oldHeatmap;
  assert.match(elements['dashboard-mini-heatmaps'].innerHTML,/case_c_surface/);
  assert.doesNotMatch(elements['dashboard-mini-heatmaps'].innerHTML,/case_b_surface/,
    'a late mini-heatmap response from the previous case must not overwrite the active case');
  console.log('dashboard request order: stale summary and mini-heatmap responses ignored PASS');
})().catch(error=>{console.error(error);process.exitCode=1;});
