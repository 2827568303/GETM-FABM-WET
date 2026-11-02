const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const html=fs.readFileSync('3DWET/app/templates/index.html','utf8');
const dashboard=html.slice(html.indexOf('id="page-dashboard"'),html.indexOf('<!-- Case Management'));
assert.match(dashboard,/for="dashboard-variable-select">主变量</,'the dashboard selector has a visible Chinese source label');
assert.match(dashboard,/aria-label="选择首页主结果变量"/,'the dashboard selector has a Chinese source accessibility label');
const context=vm.createContext({window:{},console,fetch:async()=>({ok:true,json:async()=>JSON.parse(fs.readFileSync('3DWET/app/static/i18n/en.json','utf8'))})});
vm.runInContext(fs.readFileSync('3DWET/app/static/js/i18n.js','utf8'),context);
(async()=>{
  const i=context.window.StudioI18n;await i.ready;await i.setLocale('en-US');
  assert.equal(i.t('主视图'),'Main view','primary-view metadata suffix uses the English catalog');
  assert.equal(i.t('主变量'),'Primary variable','the visible selector label uses the English catalog');
  assert.equal(i.t('选择首页主结果变量'),'Choose the dashboard primary result variable','the accessibility label uses the English catalog');
  console.log('dashboard primary variable localization: visible and accessibility labels PASS');
})().catch(error=>{console.error(error);process.exitCode=1;});
