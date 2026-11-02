const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('3DWET/app/static/js/app.js','utf8');
const container={innerHTML:'',classList:{remove(){}}};
const select={value:'',children:[],replaceChildren(...children){this.children=children;}};
const state={activeCase:'Case A',activeCasePath:'C:/cases/a',caseRevision:1};
const uiLocale={value:'en-US'};
const entries={
  temp:{mean:12,min:10,max:14,units:'°C',data:[[12]]},
  oxygen:{mean:8,min:6,max:10,units:'g/m3',data:[[8]]}
};
const context=vm.createContext({state,$:id=>id==='dashboard-mini-heatmaps'?container:id==='dashboard-variable-select'?select:null,
  window:{StudioI18n:{scientificText:(zh,en)=>uiLocale.value==='zh-CN'?zh:en}},
  document:{createElement:tag=>({tagName:tag,value:'',textContent:''})},
  api:async()=>entries,fmt:value=>String(value),resultLabel:(_,key)=>key,
  escapeHtml:value=>String(value),escapeAttr:value=>String(value),drawHeatmap(){}});
const start=source.indexOf('async function loadDashboardMiniHeatmaps(');
vm.runInContext(source.slice(start,source.indexOf('// ── 2D Visualization',start)),context);
(async()=>{
  await context.loadDashboardMiniHeatmaps();
  assert.equal(select.value,'temp','the first available result is the initial primary view without implying a preferred science variable');
  assert.match(container.innerHTML,/data-dashboard-primary="true"/,'one result is clearly rendered as the dominant primary canvas');
  assert.match(container.innerHTML,/temp · Main view/,'the selected-card suffix is localized in English while the scientific variable label remains unchanged');
  assert.match(container.innerHTML,/workbench-heatmap-title">oxygen<\/div>/,'other scientific variable labels remain unchanged');
  select.value='oxygen';select.onchange();
  assert.match(container.innerHTML,/data-dashboard-variable="oxygen"[^>]*data-dashboard-primary="true"/,'choosing another available variable moves primary emphasis to that result');
  assert.match(container.innerHTML,/oxygen · Main view/,'English localization applies after changing the primary variable');
  uiLocale.value='zh-CN';await context.loadDashboardMiniHeatmaps();
  assert.match(container.innerHTML,/oxygen · 主视图/,'the selected-card suffix remains localized in Chinese');
  assert.match(container.innerHTML,/data-dashboard-variable="temp"[^>]*data-dashboard-primary="false"/,'other result previews remain available as secondary choices');
  console.log('dashboard primary result selection: selectable dominant canvas and secondary previews PASS');
})().catch(error=>{console.error(error);process.exitCode=1;});
