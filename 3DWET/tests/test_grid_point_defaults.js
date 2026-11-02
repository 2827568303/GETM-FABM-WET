const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {test}=require('node:test');
const source=fs.readFileSync('3DWET/app/static/js/app.js','utf8');
const helperStart=source.indexOf('async function constrainPointInputsToGrid(');
const timeseriesStart=source.indexOf('async function initTimeseries(');
const timeseriesEnd=source.indexOf('\nfunction toggleTsMode()',timeseriesStart);
const vheatStart=source.indexOf('async function initVHeat(');
const vheatEnd=source.indexOf('\nfunction toggleVHeatScope()',vheatStart);
const extractStart=source.indexOf('async function extractTimeseries(');
const extractEnd=source.indexOf('// ── Vertical Heatmap',extractStart);
const updateVheatStart=source.indexOf('async function updateVHeat(');
const updateVheatEnd=source.indexOf('function _vheatDepthFrac(',updateVheatStart);
assert.ok(helperStart>=0&&timeseriesStart>helperStart&&vheatStart>timeseriesStart,
  'shared grid-bound point initialization must precede both page initializers');
assert.ok(timeseriesEnd>timeseriesStart&&vheatEnd>vheatStart,'page initializer boundaries must exist');
assert.ok(extractEnd>extractStart&&updateVheatEnd>updateVheatStart,'point request functions must exist');
const helperEnd=timeseriesStart;
const helper=source.slice(helperStart,helperEnd);
const timeseries=source.slice(timeseriesStart,timeseriesEnd);
const vheat=source.slice(vheatStart,vheatEnd);
  const extract=source.slice(extractStart,extractEnd);
  const updateVheat=source.slice(updateVheatStart,updateVheatEnd);

function environment(){
  const pending=[];
  const input=value=>({value,min:'',max:'',step:''});
  const elements={
    'ts-var':{options:{length:1},value:'temp'},
    'vheat-var':{options:[{dataset:{hasLevel:'1'}}],value:'temp',selectedIndex:0},
    'ts-i':input('12'),'ts-j':input('10'),'vheat-i':input('12'),'vheat-j':input('10'),
    'ts-mode':{value:'point'},'vheat-scope':{value:'point'},
    'ts-region':{value:'1,2,1,2'},'vheat-region':{value:'1,2,1,2'},'vheat-meta':{innerHTML:''},
  };
  const requests=[];
  const context=vm.createContext({
    state:{activeCasePath:'case-a',caseRevision:1,variables3d:[],variables2d:[]},
    $:id=>elements[id],window:{VariableGuide:{refresh(){}}},
    getScientificGeometry:()=>new Promise(resolve=>pending.push(resolve)),
    loadVariables:async()=>{},toggleVHeatScope(){},api:async url=>{requests.push(url);return {error:'sentinel'};},
    toast(){},Promise,Number,Array,Math,
  });
  vm.runInContext(helper,context);
  vm.runInContext(timeseries,context);
  vm.runInContext(vheat,context);
  vm.runInContext(extract,context);
  vm.runInContext(updateVheat,context);
  return {context,elements,pending,requests};
}

test('vheat and time-series defaults fit the active grid before requests can use them',async()=>{
  const e=environment();
  const vheatReady=e.context.initVHeat(),timeseriesReady=e.context.initTimeseries();
  assert.equal(e.pending.length,2,'both pages must resolve bounds from current scientific geometry');
  e.pending.forEach(resolve=>resolve({shape:[8,11]}));
  await Promise.all([vheatReady,timeseriesReady]);
  for(const prefix of ['vheat','ts']){
    assert.equal(e.elements[`${prefix}-i`].value,'10','i is bounded by the 11-cell X dimension');
    assert.equal(e.elements[`${prefix}-j`].value,'7','j is bounded by the 8-cell Y dimension');
    assert.equal(e.elements[`${prefix}-i`].max,'10');
    assert.equal(e.elements[`${prefix}-j`].max,'7');
    assert.equal(e.elements[`${prefix}-i`].min,'0');
    assert.equal(e.elements[`${prefix}-j`].min,'0');
  }
});

test('valid saved points are retained when grid constraints are applied',async()=>{
  const e=environment();
  e.elements['vheat-i'].value='3';e.elements['vheat-j'].value='3';
  const ready=e.context.initVHeat();
  e.pending.shift()({shape:[8,11]});
  await ready;
  assert.equal(e.elements['vheat-i'].value,'3');
  assert.equal(e.elements['vheat-j'].value,'3');
});

test('point requests wait for current grid bounds before using either page selection',async()=>{
  const e=environment();
  const timeseries=e.context.extractTimeseries();
  assert.equal(e.pending.length,1,'time series must wait for current grid geometry');
  e.pending.shift()({shape:[8,11]});
  await timeseries;
  assert.match(e.requests[0],/&i=10&j=7(?:&|$)/,'time series request must use the bounded point');

  e.requests.length=0;
  const vheat=e.context.updateVHeat();
  assert.equal(e.pending.length,1,'vertical heatmap must wait for current grid geometry');
  e.pending.shift()({shape:[8,11]});
  await vheat;
  assert.match(e.requests[0],/&i=10&j=7(?:&|$)/,'vertical heatmap request must use the bounded point');
});
