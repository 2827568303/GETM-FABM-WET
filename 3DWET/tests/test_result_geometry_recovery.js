const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const {test} = require('node:test');
const source = fs.readFileSync('3DWET/app/static/js/app.js', 'utf8');
const geometry = () => ({shape:[1,1],wetMask:[[true]],depth:[[4]],coordinate_mode:'index'});
const field = value => ({data:[[value]],shape:[1,1],min:value,max:value,mean:value});
function environment() {
    const handlers = {}, drawn = [], failures = [], published = [], hover = [], pending = [];
    const canvas = {addEventListener:(name,fn)=>handlers[name]=fn};
    const elements = {'viz2d-canvas':canvas,'viz2d-var':{value:'temp'},'viz2d-time':{value:'0'},
        'viz2d-level':{value:'0'},'viz2d-time-label':{},'viz2d-min':{},'viz2d-max':{},'viz2d-info':{},'viz2d-coord':{}};
    const context = vm.createContext({state:{caseRevision:1,activeCasePath:'A',timeLabels:[],viz2dPolygon:[],viz2dTool:'inspect'},
        window:{ScientificHeatmap:{},ScientificWorkspace:{syncFrom(){},loading(){},failure:(...args)=>failures.push(args),publish:(...args)=>published.push(args)},
            VariableGuide:{updateValues(){},valueText:(name,value)=>{hover.push({name,value});return name+':'+value;}}},
        $:id=>elements[id],ModelDates:{format:x=>x||''},fmt:String,resultLabel:(d,n)=>n,toast(){},
        drawHeatmap:(id,data)=>drawn.push(data),drawColorbar(){},getCanvasCell:()=>({i:0,j:0}),
        api:()=>new Promise((resolve,reject)=>pending.push({resolve,reject}))});
    vm.runInContext(source.slice(source.indexOf('async function getScientificGeometry('),source.indexOf('// Variable change handler')),context);
    vm.runInContext(source.slice(source.indexOf('function setupViz2dCanvasHandlers('),source.indexOf('function drawViz2dPolygonOverlay(')),context);
    return {context,elements,canvas,handlers,drawn,failures,published,hover,pending};
}
test('settled failures are retryable; concurrent requests share a pending fetch',async()=>{
    for(const reject of [false,true]) {
        const e=environment(),first=e.context.getScientificGeometry(),shared=e.context.getScientificGeometry();
        assert.equal(e.pending.length,1);
        if(reject)e.pending.shift().reject(Error('network'));else e.pending.shift().resolve({error:'temporary'});
        await Promise.allSettled([first,shared]);
        const retry=e.context.getScientificGeometry();
        assert.equal(e.pending.length,1,'a settled failure must permit a new geometry fetch');
        e.pending.shift().resolve(geometry());assert.ok(await retry);
    }
});
test('an obsolete geometry request cannot clear the current case pending request',async()=>{
    const e=environment(),old=e.context.getScientificGeometry(),a=e.pending.shift();
    e.context.state.caseRevision++;const current=e.context.getScientificGeometry(),b=e.pending.shift();
    a.resolve(geometry());await old;
    const shared=e.context.getScientificGeometry();assert.equal(e.pending.length,0);
    b.resolve(geometry());await Promise.all([current,shared]);
});
test('the global grid status follows only successfully loaded current-case geometry',async()=>{
    const e=environment();e.elements['qgis-status-grid']={textContent:'待加载'};
    const old=e.context.getScientificGeometry(),a=e.pending.shift();
    e.context.state.caseRevision++;const current=e.context.getScientificGeometry(),b=e.pending.shift();
    a.resolve({...geometry(),shape:[2,3]});await old;
    assert.equal(e.elements['qgis-status-grid'].textContent,'待加载','stale geometry cannot label the new case');
    b.resolve({...geometry(),shape:[14,21]});await current;
    assert.equal(e.elements['qgis-status-grid'].textContent,'21 × 14','result viewers have already loaded a real grid without opening the map page');
});
test('missing or mismatched geometry reports failure and preserves the last displayed result',async()=>{
    for(const bad of [{error:'unavailable'},{...geometry(),shape:[2,1]}, {...geometry(),wetMask:[]}]) {
        const e=environment(),oldField=[[15]],oldGeometry=geometry();
        e.canvas._resultField=oldField;e.canvas._scientificMetadata=oldGeometry;e.canvas._resultVariable='temp';
        e.elements['viz2d-var'].value='oxygen';
        const task=e.context.updateViz2d();e.pending.shift().resolve(field(2));
        await new Promise(resolve=>setImmediate(resolve));e.pending.shift().resolve(bad);await task;
        assert.equal(e.drawn.length,0,'invalid geometry must not replace the canvas');
        assert.equal(e.canvas._resultField,oldField);assert.equal(e.canvas._scientificMetadata,oldGeometry);
        assert.equal(e.canvas._resultVariable,'temp');assert.equal(e.published.length,0);assert.equal(e.failures.length,1);
    }
});
test('hover uses the last successfully displayed variable while a new selection fails',async()=>{
    const e=environment();let task=e.context.updateViz2d();e.pending.shift().resolve(field(15));
    await new Promise(resolve=>setImmediate(resolve));e.pending.shift().resolve(geometry());await task;
    e.context.setupViz2dCanvasHandlers();e.elements['viz2d-var'].value='oxygen';
    task=e.context.updateViz2d();e.pending.shift().resolve({error:'no output'});await task;
    e.handlers.mousemove({});assert.deepEqual(e.hover,[{name:'temp',value:15}]);
});
