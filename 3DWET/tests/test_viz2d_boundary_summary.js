const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('3DWET/app/static/js/app.js','utf8');
assert.match(source,/地理\/科学真实性未验证/,'saved outlines are never presented as geographically or scientifically validated');
assert.match(source,/仅用于显示裁切/,'2D outline status limits coordinate and mask checks to display clipping');
const summary={textContent:'old summary'};
const context=vm.createContext({
  $:id=>id==='viz2d-summary'?summary:null,
  window:{StudioI18n:{scientificText:(_zh,en)=>en}}
});
const start=source.indexOf('function setViz2dBoundarySummary(');
const end=source.indexOf('\n}',start)+2;
assert.ok(start>=0&&end>start,'the visible boundary-summary helper exists');
vm.runInContext(source.slice(start,end),context);
context.setViz2dBoundarySummary('Boundary: wet-cell edge proxy (unverified)');
assert.equal(summary.textContent,'Basin depth · m · terrain preview · Boundary: wet-cell edge proxy (unverified)',
  'the visible 2D summary explicitly identifies the fallback as an unverified proxy');

const updateStart=source.indexOf('async function updateViz2d()');
const updateEnd=source.indexOf('function setViz2dBoundarySummary(',updateStart);
const update=source.slice(updateStart,updateEnd);
const staticPublish=update.indexOf("window.ScientificWorkspace?.publish('viz2d'");
const staticSummary=update.indexOf('setViz2dBoundarySummary(outline);');
const dynamicPublish=update.indexOf("window.ScientificWorkspace?.publish('viz2d',{variable:varName,label:resultLabel");
const dynamicSummary=update.indexOf('setViz2dBoundarySummary(outline,',dynamicPublish);
assert.ok(staticPublish>=0&&staticSummary>staticPublish,'static terrain publishes its metadata before restoring the visible proxy label');
assert.ok(dynamicPublish>=0&&dynamicSummary>dynamicPublish,'result frames restore the boundary label after workspace publishing');
console.log('2D visible boundary summary and workspace-publish ordering PASS');
