const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const elements=new Map(),events={},timers=new Map(),frames=new Map();
let timerId=0,frameId=0,monoNow=0,blocked=false,release,workspace,style;
const requests=[];
function element(id){if(!elements.has(id)){const classes=new Set();elements.set(id,{id,value:'',max:'4',textContent:'',style:{},
 options:[],dataset:{},disabled:false,checked:false,classList:{toggle(k,v){if(v===undefined)v=!classes.has(k);v?classes.add(k):classes.delete(k);return v;},contains:k=>classes.has(k),remove:k=>classes.delete(k)},
 setAttribute(k,v){this[k]=String(v);},addEventListener(k,fn){this[k]=fn;},replaceChildren(){},querySelectorAll:()=>[]});}return elements.get(id);}
for(const kind of ['viz2d','viz3d']){element(kind+'-var').value='temp';element(kind+'-iso-var').value='temp';element(kind+'-time').value='0';
 element(kind+'-iso-time').value='0';element(kind+'-speed').value='1';element(kind+'-play-start').value='0';element(kind+'-play-end').value='4';
 element(kind+'-range-mode').value='auto';element(kind+'-palette').value='lake';}
element('viz3d-iso-render').value='cloud';element('viz3d-iso-overlay').checked=true;
const clock={now:()=>monoNow};
const context=vm.createContext({console,window:{performance:clock,matchMedia:query=>({matches:query.includes('1180px')}),requestAnimationFrame:fn=>{const id=++frameId;frames.set(id,fn);return id;},cancelAnimationFrame:id=>frames.delete(id),StudioIcons:{node:()=>null}},performance:clock,
 document:{readyState:'loading',hidden:false,getElementById:element,addEventListener:(k,fn)=>events[k]=fn,querySelectorAll:()=>[]},
 state:{activeCasePath:'A',activeCase:'A',caseRevision:1,timeLabels:['t0','t1','t2','t3','t4'],
  variables2d:[{name:'temp',ntimesteps:5}],variables3d:[{name:'temp',ntimesteps:5}],resultTimeAxes:{}},
 setTimeout:(fn,delay=0)=>{const id=++timerId;timers.set(id,{fn,delay});return id;},clearTimeout:id=>timers.delete(id),
 updateViz2d:async()=>{const frame=Number(element('viz2d-time').value);requests.push(['viz2d',frame]);if(blocked)await new Promise(resolve=>release=resolve);},
 updateViz3dIso:async()=>{requests.push(['viz3d',Number(element('viz3d-iso-time').value)]);},
 ModelDates:{format:x=>x},Map,Set,Number,JSON,Promise});
vm.runInContext(fs.readFileSync('3DWET/app/static/js/scientific_style.js','utf8'),context);
vm.runInContext(fs.readFileSync('3DWET/app/static/js/scientific_workspace.js','utf8'),context);
const flush=()=>new Promise(resolve=>setImmediate(resolve));
async function drainFrames(){for(let guard=0;frames.size&&guard<12;guard++){const [id,fn]=frames.entries().next().value;frames.delete(id);fn(monoNow);await flush();}}
async function fireTimer(){const [id,timer]=timers.entries().next().value||[];assert.ok(timer,'expected a pending playback timer');timers.delete(id);monoNow+=timer.delay;timer.fn();await flush();await drainFrames();}
(async()=>{
 workspace=context.window.ScientificWorkspace;style=context.window.ScientificStyle;workspace.bind();workspace.onNavigate('viz2d');
 assert.equal(element('page-viz3d').classList.contains('sw-settings-open'),false,'the 3D plot opens with advanced controls collapsed so the result stays primary');
 assert.equal(element('viz3d-settings-toggle')['aria-expanded'],'false','collapsed 3D settings are announced accessibly');
 assert.equal(element('page-viz3d').classList.contains('sw-inspector-closed'),true,'at a 1092px viewport the 3D inspector starts as a drawer so the plot keeps its width');
 workspace.publish('viz2d',{variable:'temp',label:'Temperature',units:'C',date:'t0',time:0,min:1,max:2,field:[[1,2]],range:style.resolve({caseKey:'A',variable:'temp',min:1,max:2})});
 workspace.togglePlay('viz2d');assert.equal(style.get('A','temp').mode,'auto','playback keeps per-frame automatic colour scaling');
 assert.equal(style.get('A','temp').min,null,'auto playback does not lock the initial colour minimum');
 // Initial frame renders before the first deadline; fake RAF completes presentation deterministically.
 await flush();await drainFrames();assert.deepEqual(requests,[['viz2d',0]]);assert.equal(timers.size,1);
 blocked=true;await fireTimer();assert.deepEqual(requests,[['viz2d',0],['viz2d',1]],'playback requests the next real output frame in order');
 assert.equal(element('viz2d-time').value,'1');assert.equal(timers.size,0,'a slow render holds back the scheduler instead of queuing another request');
 release();blocked=false;await flush();await drainFrames();assert.equal(timers.size,1,'the next beat is scheduled after the slow render completes');
 await fireTimer();assert.deepEqual(requests,[['viz2d',0],['viz2d',1],['viz2d',2]],'resumed playback continues through actual output frames in order');
 assert.equal(style.get('A','temp').mode,'auto','later frames preserve auto scaling');
 workspace.togglePlay('viz2d');assert.equal(timers.size,0,'pause cancels the pending timer');
 workspace.togglePlay('viz2d');assert.equal(timers.size,1,'resume schedules the next frame without re-rendering the current one');
 await fireTimer();assert.deepEqual(requests.at(-1),['viz2d',3]);
 workspace.onNavigate('viz3d');assert.equal(timers.size,0,'leaving the results view stops playback');
 context.state.caseRevision++;context.state.activeCasePath='B';workspace.onNavigate('viz2d');
 assert.equal(style.get('B','temp').mode,'auto','a different case uses its own default per-frame scaling');
 element('viz2d-range-mode').value='custom';element('viz2d-range-min').value='10';element('viz2d-range-max').value='2';
 assert.equal(workspace.applySettings('viz2d'),false);assert.equal(style.get('B','temp').mode,'auto');
 assert.ok(element('viz2d-range-status').textContent.length,'invalid custom limits have a visible explanation');
 element('viz2d-range-min').value='30';element('viz2d-range-max').value='20';element('viz2d-range-min').input();
 workspace.publish('viz2d',{variable:'temp',label:'Temperature',time:0,min:1,max:2,field:[[1,2]],range:style.resolve({caseKey:'B',variable:'temp',min:1,max:2})});
 assert.equal(element('viz2d-range-min').value,'30','a new result must not erase an in-progress range draft');
 assert.equal(element('viz2d-range-max').value,'20');assert.equal(element('viz2d-range-mode').value,'custom');
 element('viz3d-iso-render').value='waterbody';element('viz3d-iso-overlay').checked=true;
 workspace.onNavigate('viz3d');workspace.togglePlay('viz3d');await flush();await drainFrames();assert.equal(timers.size,1);
 assert.equal(style.get('B','temp').mode,'auto','3D playback also keeps per-frame automatic scaling');
 await fireTimer();assert.deepEqual(requests.slice(-2),[['viz3d',0],['viz3d',1]],'3D playback requests sequential model output frames');
 element('viz3d-iso-overlay').checked=false;workspace.syncFrom('viz3d');
 assert.equal(timers.size,0,'switching to static terrain stops model-frame playback');
 element('viz3d-palette').value='viridis';element('viz3d-range-mode').value='auto';assert.equal(workspace.applySettings('viz3d'),true);
 assert.equal(style.get('B','__bathy__').palette,'viridis','terrain preview settings apply to the displayed depth field');
 assert.equal(style.get('B','temp').palette,'lake','terrain preview settings do not alter the unshown scalar');
 assert.equal(element('viz3d-opacity').disabled,true);assert.equal(element('viz3d-iso-layer').disabled,true);
 workspace.togglePlay('viz3d');assert.equal(timers.size,0,'static terrain cannot start model-frame playback');
 console.log('Scientific workspace playback, auto range, backpressure, pause/resume, case isolation and draft validation PASS');
})().catch(error=>{console.error(error);process.exitCode=1;});
