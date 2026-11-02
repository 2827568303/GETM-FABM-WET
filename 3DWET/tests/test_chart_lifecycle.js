const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('3DWET/app/static/js/view_controls.js','utf8');
const registered=new Map(),chartBindings=new WeakMap();
let plugin,removed=0,disconnected=0,listeners=0;
const toolbar={remove(){removed++;}};
const canvas={addEventListener(){listeners++;},removeEventListener(){listeners--;},
    parentElement:{querySelector:()=>toolbar}};
const context=vm.createContext({registered,chartBindings,window:{
    addEventListener(){listeners++;},removeEventListener(){listeners--;},
    Chart:{register(p){plugin=p;}}},document:{},
    registerGraphic(el,hooks){registered.set(el,{hooks,toolbar,observer:{disconnect(){disconnected++;}}});}});
vm.runInContext(source.slice(source.indexOf('    function chartRegister('),source.indexOf('    function plotlyRegister(')),context);
vm.runInContext(source.slice(source.indexOf('    function installLibraries('),source.indexOf('    function discover(')),context);
context.installLibraries();
for(let n=0;n<5;n++) {
    const chart={canvas,scales:{},resize(){assert.ok(this.canvas,'destroyed chart resized');}};
    plugin.afterUpdate(chart);
    assert.equal(registered.size,1);
    assert.equal(listeners,4);
    // Chart.js 4 sets canvas=null before notifying the afterDestroy hook.
    chart.canvas=null;
    assert.doesNotThrow(()=>plugin.afterDestroy(chart),'destroying a real Chart.js chart must release the saved canvas');
    assert.equal(registered.size,0,'destroyed chart must not retain a resize callback');
    assert.equal(chartBindings.has(chart),false,'destroyed binding must be removed');
    assert.equal(listeners,0,'canvas/window listeners must be released');
    assert.equal(disconnected,n+1);
    assert.equal(removed,n+1);
}
assert.doesNotThrow(()=>plugin.afterDestroy({canvas:null}));
console.log('Chart.js lifecycle: null canvas cleanup, observers/listeners/toolbars, five redraws PASS');
