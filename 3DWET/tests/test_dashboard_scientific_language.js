const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('3DWET/app/static/js/app.js','utf8');
const item={name:'temp',zh_name:'水温',en_name:'Water temperature',long_name:'temperature',mean:12,min:10,max:14,units:'C',data:[[12]]};
const elements={'dashboard-vars':{},'dashboard-mini-heatmaps':{classList:{remove(){}}}};
const ctx=vm.createContext({state:{variables2d:[],variables3d:[item]},window:{StudioI18n:{variable:v=>({...v,comparison_name:'水温'}),scientificText:(zh)=>zh}},
  $:id=>elements[id],api:async()=>({temp:item}),fmt:String,drawHeatmap:()=>{}});
vm.runInContext(source.slice(source.indexOf('function localizedResult('),source.indexOf('const chartLanguageSources')),ctx);
vm.runInContext(source.slice(source.indexOf('function escapeHtml('),source.indexOf('async function resetParam(')),ctx);
vm.runInContext(source.slice(source.indexOf('async function loadDashboardSummary('),source.indexOf('// ── 2D Visualization')),ctx);
(async()=>{await ctx.loadDashboardSummary();await ctx.loadDashboardMiniHeatmaps();
  for(const id of Object.keys(elements)) {
    assert.match(elements[id].innerHTML,/水温/);
    assert.match(elements[id].innerHTML,/data-i18n-skip="true"/);
  }
  console.log('dashboard scientific language: summary and six-field labels use the selected scientific name PASS');
})().catch(e=>{console.error(e);process.exitCode=1});
