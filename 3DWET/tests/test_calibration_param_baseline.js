const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('3DWET/app/static/js/app.js','utf8');
const elements={'params-list':{innerHTML:'',rows:[],appendChild(row){this.rows.push(row);}},'param-module-select':{value:'m'},'param-saved-0':{}};
const param={name:'p',value:3,saved_value:3,default_value:1};
const context=vm.createContext({StudioIcons:{node:()=>({}),svg:()=>'<svg></svg>',setStatus:()=>{}},state:{currentParams:[param],fabmModules:[{name:'m',parameters:[param]}]},$:id=>elements[id],
    document:{createElement:()=>({})},window:{},api:async()=>({success:true}),setTimeout:()=>{},toast:()=>{}});
vm.runInContext(source.slice(source.indexOf('function renderParams('),source.indexOf('async function resetParam(')),context);
vm.runInContext(source.slice(source.indexOf('const paramSaveTimers ='),source.indexOf('// ── Time Settings')),context);
(async()=>{context.renderParams([param]);assert.doesNotMatch(elements['params-list'].rows[0].innerHTML,/param-value param-dirty/);
    assert.match(elements['params-list'].rows[0].innerHTML,/resetParam/,'reset-to-default still available');
    const input={value:'4',dataset:{idx:'0'},classList:{remove(){}}};await context.saveParam(input,'m','p');
    assert.equal(param.value,4);assert.equal(param.saved_value,4);assert.equal(input.dataset.saved,'4');
    console.log('parameter baseline: saved case values are clean; save refreshes baseline; reset remains PASS');
})().catch(e=>{console.error(e);process.exitCode=1;});

