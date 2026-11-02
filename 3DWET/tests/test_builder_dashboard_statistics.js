const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('3DWET/app/static/js/app.js', 'utf8');
function harness({delayMetadata=false}={}) {
    const elements = new Proxy({}, {get: (o,id) => o[id] ||= {value:'',textContent:'-',style:{}}});
    elements['build-dt'].value='2'; elements['build-nlev'].value='6';
    elements['stat-nlev'].textContent='10';
    const requests=[], estimates=[], metadata=[];
    const loaded={run_info:{nlev:6},fabm:{modules:[{name:'POM'}],categories:{OM:['POM']},total_modules:20}};
    const context=vm.createContext({StudioIcons:{node:()=>({}),svg:()=>'<svg></svg>',setStatus:()=>{}},state:{activeCase:'Fresh lake',activeCasePath:'C:/cases/Fresh lake',caseRevision:1,engines:[]},
        $:id=>elements[id], setNlev:n=>context.state.nlev=n,
        _readModelPeriod:()=>({start:'2020-01-01 00:00:00',stop:'2020-01-01 00:20:00'}),
        confirmStudio:async()=>true, _ppStatus(){},toast(){},loadInputData(){},loadCases(){},renderModuleCards(){},loadParamModules(){},
        api:async (url,options)=>{
            requests.push(url);
            if(url==='/api/case/build')return {preset_label:'Test',params_applied:2,files:['getm.inp','fabm.yaml']};
            if(url==='/api/case/load')return delayMetadata?new Promise(resolve=>metadata.push(()=>resolve(loaded))):loaded;
            if(url==='/api/run/estimate')return new Promise(resolve=>estimates.push(resolve));
            throw Error(url);
        }});
    const start=source.indexOf('function refreshCaseStatistics(');
    if(start>=0)vm.runInContext(source.slice(start,source.indexOf('function applyLoadedCase(',start)),context);
    const build=source.indexOf('async function buildCase(');
    vm.runInContext(source.slice(build,source.indexOf('// ── Modules',build)),context);
    return {context,elements,requests,estimates,metadata,loaded};
}
(async()=>{
    const h=harness();await h.context.buildCase();
    assert.equal(h.elements['stat-nlev'].textContent,6,'Builder kept pre-build vertical layers');
    assert.equal(h.context.state.nlev,6,'Layer controls retained pre-build metadata');
    assert.equal(h.elements['stat-modules'].textContent,20,'Builder kept empty module statistics');
    assert.equal(h.estimates.length,1,'Builder did not request actual wet-cell count');
    h.estimates.shift()({nwater:166});await new Promise(resolve=>setImmediate(resolve));
    assert.equal(h.elements['stat-water'].textContent,'166');
    const switched=harness();await switched.context.buildCase();
    switched.context.state.activeCasePath='C:/cases/Other';switched.context.state.caseRevision++;
    switched.elements['stat-water'].textContent='222';
    switched.estimates.shift()({nwater:166});await new Promise(resolve=>setImmediate(resolve));
    assert.equal(switched.elements['stat-water'].textContent,'222','Late estimate replaced another case');
    const same=harness();
    same.context.refreshCaseStatistics(same.loaded);
    same.context.refreshCaseStatistics(same.loaded);
    same.estimates[1]({nwater:166});await new Promise(resolve=>setImmediate(resolve));
    same.estimates[0]({nwater:0});await new Promise(resolve=>setImmediate(resolve));
    assert.equal(same.elements['stat-water'].textContent,'166','Old same-case estimate replaced newer metadata');
    const late=harness({delayMetadata:true});const building=late.context.buildCase();
    await new Promise(resolve=>setImmediate(resolve));assert.equal(late.metadata.length,1);
    late.context.state.activeCase='Other';late.context.state.activeCasePath='C:/cases/Other';late.context.state.caseRevision++;
    late.elements['stat-nlev'].textContent='12';late.elements['stat-modules'].textContent='8';
    late.metadata.shift()();await building;
    assert.equal(late.elements['stat-nlev'].textContent,'12','Old build metadata replaced another case layers');
    assert.equal(late.elements['stat-modules'].textContent,'8','Old build metadata replaced another case modules');
    console.log('Builder dashboard: actual layers/modules/wet cells; stale estimates ignored PASS');
})().catch(error=>{console.error(error);process.exitCode=1;});
