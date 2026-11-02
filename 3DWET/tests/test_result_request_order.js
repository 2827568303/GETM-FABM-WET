const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('3DWET/app/static/js/app.js','utf8');
const pending=[],drawn=[],errors=[];
function select(value='') {return {_value:value,options:[],set innerHTML(v){this.options=[];this._value='';},get value(){return this._value;},set value(v){this._value=v;},appendChild(o){this.options.push(o);if(this.options.length===1)this._value=o.value;}};}
const elements={'viz2d-var':select('temp'),'viz2d-time':{value:'0'},'viz2d-level':{value:'5'},'stat-timesteps':{},'viz2d-time-label':{},'viz2d-canvas':{},'viz2d-min':{},'viz2d-max':{},'viz2d-info':{}};
const context=vm.createContext({state:{activeCase:'A',activeCasePath:'A',caseRevision:1,variables2d:[],variables3d:[{name:'temp'}],timeLabels:[]},window:{},
 $:id=>elements[id],document:{createElement:()=>({dataset:{}})},api:()=>new Promise(resolve=>pending.push(resolve)),
 localizedVariableLabel:v=>v.name,populateCalibrationVariables:()=>{},ModelDates:{format:v=>v||''},fmt:String,
 resultLabel:(d,n)=>n,drawHeatmap:(id,data)=>drawn.push(data),drawColorbar:()=>{},toast:m=>errors.push(m)});
const inventoryStart=source.indexOf('const resultInventoryRequests = new Map();');
const inventoryEnd=source.indexOf('\nfunction clearResultInventory',inventoryStart);
vm.runInContext(source.slice(inventoryStart,inventoryEnd),context);
const priorityStart=source.indexOf('function resultVariablePriority(');
const priorityEnd=source.indexOf('\nfunction hasVerticalResultDimension',priorityStart);
vm.runInContext(source.slice(priorityStart,priorityEnd),context);
const verticalStart=source.indexOf('function hasVerticalResultDimension(');
const verticalEnd=source.indexOf('\nfunction resultVariableOptionLabel',verticalStart);
vm.runInContext(source.slice(verticalStart,verticalEnd),context);
const labelStart=source.indexOf('function resultVariableOptionLabel(');
const labelEnd=source.indexOf('// ── Utilities',labelStart);
vm.runInContext(source.slice(labelStart,labelEnd),context);
context.verticalResultSelectIds=new Set(['viz3d-var','viz3d-avg-var']);
vm.runInContext(source.slice(source.indexOf('async function loadVariables('),source.indexOf('// ── Dashboard')),context);
vm.runInContext(source.slice(source.indexOf('async function updateViz2d('),source.indexOf('// Variable change handler')),context);
const variables=name=>({'3d':[{name:'D'},{name:name||'temp'}],timesteps_3d:20});
const field=value=>({data:[[value]],min:value,max:value,mean:value,shape:[1,1]});
(async()=>{
 let task=context.loadVariables();pending.shift()(variables());await task;
 assert.equal(elements['viz2d-var'].value,'temp','refresh must preserve the current selection');
 const old=context.loadVariables();
 const fresh=context.loadVariables();
 assert.equal(pending.length,1,'same-case inventory requests share one in-flight API read');
 pending.shift()(variables('salinity'));await Promise.all([fresh,old]);
 assert.equal(context.state.variables3d[1].name,'salinity','late old inventory must not replace newer data');
 task=context.loadVariables();const resolve=pending.shift();context.state.caseRevision++;resolve(variables('foreign'));await task;
 assert.equal(context.state.variables3d[1].name,'salinity','previous case inventory must be ignored');
 elements['viz2d-var'].value='temp';let first=context.updateViz2d();const firstResolve=pending.shift();
 elements['viz2d-var'].value='D';let second=context.updateViz2d();pending.shift()(field(2));await second;
 firstResolve(field(1));await first;
 assert.deepEqual(drawn,[[[2]]],'late field response must never overwrite the chosen variable');
 first=context.updateViz2d();const staleError=pending.shift();second=context.updateViz2d();pending.shift()(field(3));await second;
 staleError({error:'outdated error'});await first;assert.deepEqual(errors,[],'obsolete failures must not show a misleading toast');
 first=context.updateViz2d();const staleCase=pending.shift();context.state.caseRevision++;staleCase(field(4));await first;
 assert.deepEqual(drawn,[[[2]],[[3]]],'a field from the previous case must not render');
 console.log('Result requests: preserve selection, latest inventory/field wins, obsolete errors and cases ignored PASS');
})().catch(e=>{console.error(e);process.exitCode=1;});
