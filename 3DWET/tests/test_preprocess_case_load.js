const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const source = fs.readFileSync('3DWET/app/static/js/preprocess.js', 'utf8');
const save = source.slice(source.indexOf('async function saveBathymetry()'),
    source.indexOf('// ── Canvas drawing helpers'));
const path = 'C:/model/case/New Lake';
const elements = {
    'pp-case-name': {value:'New Lake'}, 'pp-lake-name': {value:'Lake'},
    'pp-depth-info': {innerHTML:''}, 'case-badge': {style:{}}, 'footer-status': {},
};
let loads = [], navigation = [], statuses = [], loadSuccess = true, saveError = false;
const state = {activeCase:'Old Lake', activeCasePath:'C:/model/case/Old Lake',
    fabmModules:[{name:'old'}], preprocess:{grid_id:'grid', depth_array:[[3]], rivers:[]}};
const context = vm.createContext({StudioIcons:{node:()=>({}),svg:()=>'<svg></svg>',setStatus:()=>{}},state, document:{getElementById:id=>elements[id]},
    _ppStatus:(...args)=>statuses.push(args), navigate:page=>navigation.push(page),
    api:async()=>saveError ? {error:'write denied'} : {case_name:'New Lake',
        path:path+'/bathymetry.nc', n_water_cells:1, lake_area_m2:2500},
    loadCase:async name=>{
        loads.push(name);
        if(!loadSuccess) return false;
        state.activeCase=name; state.activeCasePath=path;
        state.fabmModules=[];
        elements['footer-status'].textContent='案例: '+name;
        navigation.push('dashboard');
        return true;
    }});
vm.runInContext(save, context);
(async()=>{
    await context.saveBathymetry();
    assert.deepEqual(loads,['New Lake'],'saving must use the common case loader');
    assert.equal(state.activeCasePath,path,'the complete case path must be loaded');
    assert.deepEqual(state.fabmModules,[],'previous case modules must be replaced');
    assert.equal(navigation.at(-1),'preprocess','keep the saved preview visible');
    assert.match(elements['pp-depth-info'].innerHTML,/已加载/);
    const previousPreview=elements['pp-depth-info'].innerHTML;
    loadSuccess=false;
    await context.saveBathymetry();
    assert.equal(elements['pp-depth-info'].innerHTML,previousPreview,
        'a failed case load must not append a success claim');
    assert.equal(statuses.at(-1)[2],false);
    saveError=true;
    const before=loads.length;
    await context.saveBathymetry();
    assert.equal(loads.length,before,'failed save must not load a case');
    console.log('preprocess case load: common state, saved preview and failure handling PASS');
})().catch(error=>{console.error(error);process.exitCode=1;});
