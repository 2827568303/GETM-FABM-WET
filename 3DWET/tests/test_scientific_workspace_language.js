const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const html=fs.readFileSync('3DWET/app/templates/index.html','utf8');
const section=html.slice(html.indexOf('id="page-viz2d"'),html.indexOf('id="page-vheat"'));
const texts=new Set([...section.matchAll(/>([^<>]*[\u3400-\u9fff][^<>]*)</g)].map(m=>m[1].trim()).filter(Boolean));
for(const m of section.matchAll(/(?:title|aria-label|placeholder)="([^"]*[\u3400-\u9fff][^"]*)"/g))texts.add(m[1]);
const renderer=fs.readFileSync('3DWET/app/static/js/viz3d.js','utf8');
for(const m of renderer.matchAll(/viz3d(?:Loading|Error)\('([^']*[\u3400-\u9fff][^']*)'/g))texts.add(m[1]);
for(const text of ['2020-DOY001 00:01:00 · 层 5/5 · 垂向 13.6× · 自动范围 · 原网格 6×14×21 · 采样步长 1×1×1',
 '静态地形 · 水深 (m) · 垂向 13.6× · 自定义范围',
 '透明叠层/切片会混色；定量读色请使用不透明单层','透明点云会混色；定量读色请使用不透明显示',
 '透明等值面会混色；定量读色请使用不透明显示','透明表面会混色；定量读色请使用不透明显示',
 '透明剖面会混色；定量读色请使用不透明显示','加载失败: Network error · 保留旧图：temp · 2020-DOY001',
 '全部层等值面','湿网格岸线（采样代理，未验证）'])texts.add(text);
const context=vm.createContext({window:{},console,fetch:async()=>({ok:true,json:async()=>JSON.parse(fs.readFileSync('3DWET/app/static/i18n/en.json','utf8'))})});
vm.runInContext(fs.readFileSync('3DWET/app/static/js/i18n.js','utf8'),context);
(async()=>{
 const i=context.window.StudioI18n;await i.ready;await i.setLocale('en-US');
 const expectedTranslations=new Map([
  ['检查器','Inspector'],
  ['变量与图层','Variables and layers'],
  ['变量与视图','Variables and view'],
  ['拖动旋转，滚轮缩放；镜头仰角控制视角，垂向放大只改变显示比例。','Drag to rotate and scroll to zoom; camera elevation controls the view angle, while vertical exaggeration changes only the display scale.'],
  ['展开或收起变量、图例与显示控制','Expand or collapse variable, legend, and display controls'],
  ['展开或收起变量、镜头与图层控制','Expand or collapse variable, camera, and layer controls']
 ]);
 for(const [source,translation] of expectedTranslations)assert.equal(i.t(source),translation,'English scientific workspace translation: '+source);
 const missing=[...texts].filter(text=>/[\u3400-\u9fff]/.test(i.t(text)));
 assert.deepEqual(missing,[],'every static scientific workspace label, help and accessibility name needs an English rendering');
 console.log('Scientific workspace English static labels and accessibility text PASS ('+texts.size+' strings)');
})().catch(e=>{console.error(e);process.exitCode=1;});
