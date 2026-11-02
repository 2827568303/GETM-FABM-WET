const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {test}=require('node:test');
const source=fs.readFileSync('3DWET/app/static/js/app.js','utf8');
const initializers=source.slice(source.indexOf('async function initViz3d('),source.indexOf('async function updateViz3dIso('));
function environment(axis='xz') {
    const calls=[],listeners=new Map(),pending=[];
    const element=(value)=>({value,max:'',addEventListener(name,fn){if(!listeners.has(this))listeners.set(this,new Map());
        const list=listeners.get(this);if(!list.has(name))list.set(name,new Set());list.get(name).add(fn);},
        removeEventListener(name,fn){listeners.get(this)?.get(name)?.delete(fn);},
        dispatch(name){listeners.get(this)?.get(name)?.forEach(fn=>fn());}});
    const elements={'viz3d-section-axis':element(axis),'viz3d-section-index':element('0')};
    const state={activeCasePath:'A',caseRevision:1,variables3d:[{name:'temp',ndim:4}]};
    const context=vm.createContext({state,$:id=>elements[id],window:{ScientificWorkspace:{activate(){}}},
        document:{querySelector:()=>({open:true})},
        getScientificGeometry:()=>new Promise((resolve,reject)=>pending.push({resolve,reject})),
        updateViz3d:()=>calls.push('profile'),updateViz3dAvg:()=>calls.push('average'),
        updateViz3dIso:async()=>{calls.push('main');await context.updateSpatialSection();},
        updateSpatialSection:async()=>calls.push(['section',elements['viz3d-section-axis'].value,elements['viz3d-section-index'].value]),
        Promise,Number,Array,Math});
    vm.runInContext(initializers,context);
    return {context,state,elements,calls,pending,listeners,init:()=>context.initViz3d()};
}
const grid=mask=>({shape:[mask.length,mask[0].length],wetMask:mask});
const wetGrid=()=>grid([
    [false,false,false,false,false,false,false],
    [false,false,true,true,false,false,false],
    [false,false,false,false,false,false,false],
    [false,false,false,true,true,false,false],
    [false,false,false,false,false,false,false],
]);
test('a terrain preview does not request empty point-profile or mean-field selections',async()=>{
    const e=environment(),task=e.init();e.pending.shift().resolve(wetGrid());await task;
    assert.ok(!e.calls.includes('profile') && !e.calls.includes('average'),'empty analysis selectors must not create spurious missing-output errors');
    assert.ok(e.calls.includes('main'));
});

test('new cases choose the nearest central wet original row for XZ and column for YZ',async()=>{
    for(const [axis,expected] of [['xz','1'],['yz','3']]) {
        const e=environment(axis),task=e.init();
        assert.equal(e.pending.length,1,'initialization must read the true full-resolution wet mask');
        assert.equal(e.calls.includes('main'),false,'the first automatic section must wait for a valid default index');
        e.pending.shift().resolve(wetGrid());await task;
        assert.equal(e.elements['viz3d-section-index'].value,expected);
        assert.deepEqual(e.calls.at(-1),['section',axis,expected]);
    }
});

test('same-case reentry retains the user section and new cases initialize independently',async()=>{
    const e=environment(),first=e.init();assert.equal(e.pending.length,1);
    e.pending.shift().resolve(wetGrid());await first;e.elements['viz3d-section-index'].value='3';
    await e.init();assert.equal(e.pending.length,0);assert.equal(e.elements['viz3d-section-index'].value,'3');
    e.state.activeCasePath='B';e.state.caseRevision++;const second=e.init();assert.equal(e.pending.length,1);
    e.pending.shift().resolve(wetGrid());await second;assert.equal(e.elements['viz3d-section-index'].value,'1');
});

test('concurrent first entry waits on the same default calculation',async()=>{
    const e=environment(),first=e.init(),second=e.init();
    await new Promise(resolve=>setImmediate(resolve));
    assert.equal(e.pending.length,1,'same-case entry must share the pending geometry selection');
    assert.equal(e.calls.includes('main'),false,'a second entry cannot render the old dry-border default');
    e.pending.shift().resolve(wetGrid());await Promise.all([first,second]);
    assert.equal(e.elements['viz3d-section-index'].value,'1');
});

test('geometry lookup begins alongside inventory loading before the first main render',async()=>{
    const e=environment(),inventory=[];e.state.variables3d=[];
    e.context.loadVariables=()=>new Promise(resolve=>inventory.push(resolve));
    const task=e.init();assert.equal(e.pending.length,1);assert.equal(inventory.length,1);
    e.pending.shift().resolve(wetGrid());await new Promise(resolve=>setImmediate(resolve));
    assert.equal(e.calls.includes('main'),false,'inventory still gates the first main render');
    inventory.shift()();await task;assert.deepEqual(e.calls.at(-1),['section','xz','1']);
});

test('edits during geometry loading are never overwritten, including edit-and-revert',async()=>{
    for(const editedControl of ['viz3d-section-index','viz3d-section-axis']) {
        const e=environment(),task=e.init();assert.equal(e.pending.length,1);
        const control=e.elements[editedControl],original=control.value;
        control.value=editedControl.endsWith('axis')?'yz':'3';control.dispatch('input');control.value=original;
        e.pending.shift().resolve(wetGrid());await task;
        assert.equal(e.elements['viz3d-section-index'].value,'0');
        assert.deepEqual(e.calls.at(-1),['section','xz','0'],'only the existing renderer observes the retained user selection');
        for(const events of e.listeners.values())for(const registered of events.values())assert.equal(registered.size,0,'temporary edit listeners are removed');
    }
});

test('obsolete cases and missing geometry leave manual selection intact and main render available',async()=>{
    for(const outcome of ['case','failure','dry','invalid']) {
        const e=environment(),task=e.init();assert.equal(e.pending.length,1);const pending=e.pending.shift();
        if(outcome==='case'){e.state.caseRevision++;pending.resolve(wetGrid());}
        if(outcome==='failure')pending.reject(Error('geometry unavailable'));
        if(outcome==='dry')pending.resolve(grid([[false,false],[false,false]]));
        if(outcome==='invalid')pending.resolve({shape:[2,3],wetMask:[[true],[false,false]]});
        await task;assert.equal(e.elements['viz3d-section-index'].value,'0');
        assert.equal(e.calls.includes('main'),outcome!=='case','geometry errors do not block a current-case main render');
        if(outcome!=='case')assert.deepEqual(e.calls.at(-1),['section','xz','0']);
    }
});

test('failed, invalid and all-dry geometry allow a same-case entry to retry successfully',async()=>{
    for(const outcome of ['failure','invalid','dry']) {
        const e=environment(),first=e.init(),pending=e.pending.shift();
        if(outcome==='failure')pending.reject(Error('temporary geometry failure'));
        if(outcome==='invalid')pending.resolve({shape:[2,2],wetMask:[[true]]});
        if(outcome==='dry')pending.resolve(grid([[false,false],[false,false]]));
        await first;assert.ok(e.calls.includes('main'),'a temporary geometry problem does not block the main figure');
        const retry=e.init();assert.equal(e.pending.length,1,outcome+': an unsuccessful default remains retryable');
        e.pending.shift().resolve(wetGrid());await retry;
        assert.equal(e.elements['viz3d-section-index'].value,'1');assert.deepEqual(e.calls.at(-1),['section','xz','1']);
    }
});

test('a user edit followed by a failed geometry lookup completes default selection without later override',async()=>{
    const e=environment(),first=e.init();e.elements['viz3d-section-index'].value='3';e.elements['viz3d-section-index'].dispatch('change');
    e.pending.shift().reject(Error('temporary geometry failure'));await first;
    await e.init();assert.equal(e.pending.length,0);assert.equal(e.elements['viz3d-section-index'].value,'3');
});

test('an obsolete failed lookup cannot clear the newer case completed default',async()=>{
    const e=environment(),old=e.init(),oldGeometry=e.pending.shift();
    e.state.activeCasePath='B';e.state.caseRevision++;const current=e.init();e.pending.shift().resolve(wetGrid());await current;
    const completed=e.state.scientificSectionDefaultKey;e.elements['viz3d-section-index'].value='3';
    oldGeometry.reject(Error('old case lookup failed'));await old;
    assert.equal(e.state.scientificSectionDefaultKey,completed);
    await e.init();assert.equal(e.pending.length,0);assert.equal(e.elements['viz3d-section-index'].value,'3');
});
