const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const context=vm.createContext({window:{},console,Intl,Map,Set,WeakMap,JSON,Promise,
    localStorage:{getItem:()=>null,setItem:()=>{}},
    fetch:async()=>({ok:true,json:async()=>JSON.parse(fs.readFileSync('3DWET/app/static/i18n/en.json','utf8'))})});
vm.runInContext(fs.readFileSync('3DWET/app/static/js/i18n.js','utf8'),context);
(async()=>{
    const i=context.window.StudioI18n;await i.ready;
    assert.equal(i.scientificText('水温','Water temperature'),'水温');
    await i.setLocale('en-US');
    assert.equal(i.scientificText('水温','Water temperature'),'Water temperature');
    const variable=i.variable({zh_name:'水温',en_name:'Water temperature',meaning:'水体温度',meaning_en:'Temperature of water'});
    assert.equal(variable.comparison_name,'Water temperature');
    assert.equal(variable.comparison_meaning,'Temperature of water');
    i.importPack({locale:'fr-FR',name:'Français',messages:{'水温':'Température'}});
    await i.setLocale('fr-FR');
    assert.equal(i.scientificText('水温','Water temperature'),'Température');
    assert.equal(i.scientificText('独有的模型解释','Unique model explanation'),'Unique model explanation','missing imported terms use authored English metadata');
    assert.equal(i.scientificText('水体温度','Temperature of water'),'Temperature of water');
    assert.equal(i.scientificText('temp','temp'),'temp');
    assert.equal(i.scientificText('',''), '');
    await i.setLocale('zh-CN');
    assert.equal(i.scientificText('水温','Water temperature'),'水温','switching back must not accumulate translations');
    assert.equal(i.scientificText('','Water temperature'),'Water temperature','missing Chinese metadata retains available source');
    console.log('scientific language: selected language only, imported metadata fallback, reversible switches PASS');
})().catch(e=>{console.error(e);process.exitCode=1;});
