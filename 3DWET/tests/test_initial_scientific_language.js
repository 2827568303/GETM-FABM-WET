const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('3DWET/app/static/js/app.js','utf8');
const elements={'ic-wq-modules':{innerHTML:''},'ic-wq-search':{value:''}};
const context=vm.createContext({StudioIcons:{node:()=>({}),svg:()=>'<svg></svg>',setStatus:()=>{}},state:{icData:{modules:[{name:'POM',category:'碎屑',category_en:'Detritus',init:{sDW:2},docs:{sDW:{zh:'水中颗粒有机物',desc_en:'Particulate organic matter in water',unit:'g/m³'}},long_name:'particulate organic matter',desc:'颗粒有机物',desc_en:'Particulate organic matter pool'}]}},
  $:id=>elements[id],window:{StudioI18n:{scientificText:(zh,en)=>en||zh}},
  icPresetVarMap:()=>({sDW:'icv-sDW'}),renderIcExtraVars:()=>{}});
vm.runInContext(source.slice(source.indexOf('function escapeHtml('),source.indexOf('async function resetParam(')),context);
vm.runInContext(source.slice(source.indexOf('function renderIcWaterQuality('),source.indexOf('// Variables that are not declared')),context);
context.renderIcWaterQuality();
assert.match(elements['ic-wq-modules'].innerHTML,/Particulate organic matter in water<\/span>/);
assert.match(elements['ic-wq-modules'].innerHTML,/data-scientific-zh="水中颗粒有机物"/);
assert.match(elements['ic-wq-modules'].innerHTML,/data-scientific-en="Particulate organic matter in water"/);
assert.match(elements['ic-wq-modules'].innerHTML,/data-i18n-skip="true"/);
assert.match(elements['ic-wq-modules'].innerHTML,/Particulate organic matter pool<\/span>/,'module purpose must be visibly translated');
assert.match(elements['ic-wq-modules'].innerHTML,/>Detritus<\/div>/,'category must be visibly translated');
elements['ic-wq-search'].value='pool';context.renderIcWaterQuality();
assert.match(elements['ic-wq-modules'].innerHTML,/icv-POM-sDW/,'English module description is searchable');
console.log('initial conditions show only selected English descriptions and retain source metadata PASS');
