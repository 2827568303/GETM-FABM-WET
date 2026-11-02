// Exercise the real controller and renderer together across a delayed API reply.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {test}=require('node:test');
const app=fs.readFileSync('3DWET/app/static/js/app.js','utf8');
const start=app.indexOf('async function updateViz3dIso()'),end=app.indexOf('async function updateViz3d()',start);
const volume={shape:[2,2,2],xc:[0,100],yc:[0,100],bottom:[[4,8],[4,8]],sigma:[-.75,-.25],
 data:[[[0,1],[0,1]],[[2,3],[2,3]]],min:0,max:3,units:'Celsius'};
function environment(){
 let resolve;const response=new Promise(r=>resolve=r),published=[],plots=[],failures=[];
 const graph={innerHTML:'',dataset:{},on(){}},status={dataset:{},textContent:''};
 const controls={'viz3d-iso-var':{value:'temp'},'viz3d-iso-time':{value:'0'},'viz3d-iso-render':{value:'cloud'}};
 const metadata=[{name:'temp',ndim:4,nlev:2},{name:'elev',ndim:3},{name:'salt',ndim:4,nlev:2}];
 const Plotly={newPlot:async(_,traces,layout)=>{plots.push({traces,layout});graph._fullLayout=layout;},
  react:async(_,traces,layout)=>{plots.push({traces,layout});graph._fullLayout=layout;}};
 const window={Plotly,ScientificWorkspace:{syncFrom(){},dateLabel:()=> '2020-01-01 00:01:00',
  variableMetadata:name=>metadata.find(m=>m.name===name),current:()=>null,
  publish:(_,meta)=>published.push(meta),failure:(_,message)=>failures.push(message)}};
 const context=vm.createContext({console,window,Plotly,$:id=>controls[id],ModelDates:{format:x=>x},toast(){},
  state:{caseRevision:1,activeCase:'Lake A',activeCasePath:'A',variables3d:metadata},
  document:{getElementById:id=>id==='viz3d-plotly'?graph:id==='viz3d-status'?status:null,querySelector:()=>null},
  fetch:()=>response});
 const verticalStart=app.indexOf('function hasVerticalResultDimension('),verticalEnd=app.indexOf('\nfunction resultVariableOptionLabel',verticalStart);
 vm.runInContext(app.slice(verticalStart,verticalEnd),context);
 vm.runInContext(fs.readFileSync('3DWET/app/static/js/viz3d.js','utf8'),context);
 context.render3DCloud=context.window.render3DCloud;
 vm.runInContext(app.slice(start,end),context);
 return {context,controls,graph,status,plots,published,failures,resolve:()=>resolve({json:async()=>volume})};
}

test('a scalar surface selection supersedes an older pending volume request',async()=>{
 const e=environment(),old=e.context.updateViz3dIso();await new Promise(r=>setImmediate(r));
 e.controls['viz3d-iso-var'].value='elev';const current=e.context.updateViz3dIso();
 assert.equal(e.controls['viz3d-iso-render'].value,'surface2d');
 e.resolve();await Promise.all([old,current]);
 assert.equal(e.published.length,0,'the old temp result cannot publish ready after rejecting elev');
 assert.equal(e.plots.length,0,'a reply for the previous selection cannot newly draw the graph');
 assert.equal(e.failures.length,0,'a supported variable-height surface is not an invalid-selection error');
});

test('a valid volume choice after scalar surface mode renders without stale request poisoning',async()=>{
 const e=environment();e.controls['viz3d-iso-render'].value='surface2d';
 e.controls['viz3d-iso-render'].value='cloud';
 e.controls['viz3d-iso-var'].value='salt';
 e.context.render3DCloud=async(variable)=>{e.published.push({variable});e.plots.push({});e.graph._viz3dStatus={phase:'ready'};};
 await e.context.updateViz3dIso();
 assert.deepEqual(e.published.map(m=>m.variable),['salt']);assert.equal(e.plots.length,1);
 assert.equal(e.graph._viz3dStatus.phase,'ready');
});
