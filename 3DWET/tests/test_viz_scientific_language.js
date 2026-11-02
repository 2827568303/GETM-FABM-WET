const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const container={innerHTML:''};
const plots=[];
const payload={axis:'xz',index:0,time:0,data:[[5]],horizontal:[10],horizontal_edges:[5,15],
    depth:[[2]],depth_edges:[[4],[0]],coordinate_units:'m',depth_source:'hn',
    zh_name:'水温',long_name:'水温',long_name_en:'Water temperature',units:'degC',min:5,max:5};
const Plotly={newPlot:async(c,traces,layout)=>plots.push({traces,layout})};
const context=vm.createContext({console,window:{Plotly},Plotly,Intl,Map,Set,WeakMap,JSON,Promise,
    localStorage:{getItem:()=>null,setItem:()=>{}},CustomEvent:class {},
    document:{getElementById:()=>container,documentElement:{},readyState:'loading',
        addEventListener:()=>{},dispatchEvent:()=>{}},
    fetch:async url=>({ok:true,json:async()=>url.includes('/api/results/') ? payload :
        JSON.parse(fs.readFileSync('3DWET/app/static/i18n/en.json','utf8'))})});
vm.runInContext(fs.readFileSync('3DWET/app/static/js/i18n.js','utf8'),context);
const appSource=fs.readFileSync('3DWET/app/static/js/app.js','utf8');
vm.runInContext(appSource.slice(0,appSource.indexOf('function localizedVariableLabel')),context);
vm.runInContext("state.variables3d=[{name:'temp',zh_name:'水温',en_name:'Water temperature'}]; window.localizedResult=localizedResult;window.translateChartLabels=translateChartLabels;",context);
vm.runInContext(fs.readFileSync('3DWET/app/static/js/viz3d.js','utf8'),context);
(async()=>{
    const i=context.window.StudioI18n;await i.ready;
    await i.setLocale('en-US');
    vm.runInContext("state.variables3d.push({name:'D',zh_name:'水深',en_name:'Water depth'});",context);
    assert.equal(context.viz3dTranslateText({name:'湖盆水深'}).name,'Lake bed depth',
        'a complete structural label must not be fragmented by a shorter scientific variable name');
    await context.renderSpatialSection('temp',0,'xz',0);
    assert.ok(plots[0].layout.title.text.includes('Water temperature'),
        'Plotly title must use only the selected scientific language');
    assert.ok(plots[0].traces[0].hovertemplate.includes('Water temperature'));
    assert.ok(!plots[0].layout.title.text.includes('水温'),'English title must not append Chinese');
    assert.ok(!plots[0].traces[0].hovertemplate.includes('水温'));
    assert.equal(context.viz3dLabel(payload,'temp'),'Water temperature',
        'all 3D scientific labels follow the selected language');
    payload.long_name_en='original model temperature field';
    await context.renderSpatialSection('temp',0,'xz',0);
    assert.ok(plots[1].layout.title.text.startsWith('Water temperature<br>'),
        'section title uses the same localized metadata label as other 3D views');
    payload.long_name_en='Water temperature';
    await i.setLocale('zh-CN');
    await context.renderSpatialSection('temp',0,'xz',0);
    assert.ok(plots[2].layout.title.text.includes('水温'));
    assert.ok(!plots[2].layout.title.text.includes('Water temperature'));
    i.importPack({locale:'fr-FR',name:'Français',messages:{'水温':'Température'}});
    await i.setLocale('fr-FR');
    await context.renderSpatialSection('temp',0,'xz',0);
    assert.ok(plots[3].layout.title.text.includes('Température'));
    assert.ok(!plots[3].layout.title.text.includes('水温'));
    assert.ok(!plots[3].layout.title.text.includes('Water temperature'));
    console.log('Plotly scientific labels switch between English, Chinese and imported language PASS');
})().catch(error=>{console.error(error);process.exitCode=1;});
