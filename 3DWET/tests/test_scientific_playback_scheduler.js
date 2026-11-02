const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const {test}=require('node:test');

const source=fs.readFileSync('3DWET/app/static/js/scientific_workspace.js','utf8');
const flush=()=>new Promise(resolve=>setImmediate(resolve));

function env(kind,{stallFrames=false}={}){
 const nodes=new Map(),timers=new Map(),frames=new Map(),requests=[];
 let now=0,timerId=0,frameId=0;
 function element(id){
  if(!nodes.has(id))nodes.set(id,{id,value:'',textContent:'',dataset:{},style:{},options:[],handlers:{},replaceChildren(){},
   setAttribute(k,v){this[k]=String(v);},removeAttribute(k){delete this[k];},
   addEventListener(k,fn){(this.handlers[k]??=[]).push(fn);},
   dispatch(k){for(const fn of this.handlers[k]||[])fn({target:this});},
   classList:{toggle(){return false;},remove(){},contains(){return false;}}});
  return nodes.get(id);
 }
 const state={activeCasePath:'case',caseRevision:1,
  variables3d:[{name:'temp',time_axis:'volume',ntimesteps:4}],
  variables2d:[{name:'temp',time_axis:'volume',ntimesteps:4}],
  resultTimeAxes:{volume:['t0','t1','t2','t3']}};
 for(const name of ['viz2d','viz3d']){
  element(name==='viz2d'?'viz2d-var':'viz3d-iso-var').value='temp';
  element(name==='viz2d'?'viz2d-time':'viz3d-iso-time').value='0';
  element(name+'-speed').value='12';
  element(name+'-play-start').value='0';element(name+'-play-end').value='3';
  element(name+'-time-slider').value='0';
 }
 element('viz3d-iso-render').value='cloud';element('viz3d-iso-overlay').checked=true;
 const clock={now:()=>now};
 const context=vm.createContext({window:{performance:clock,StudioIcons:{node:()=>({})},requestAnimationFrame:callback=>{
   const id=++frameId;frames.set(id,callback);return id;
  },cancelAnimationFrame:id=>frames.delete(id)},state,console,performance:clock,
  document:{readyState:'loading',hidden:false,getElementById:element,addEventListener(){},querySelectorAll:()=>[]},
  ModelDates:{format:value=>value},
  setTimeout:(fn,delay=0)=>{const id=++timerId;timers.set(id,{fn,delay});return id;},
  clearTimeout:id=>timers.delete(id),
  updateViz2d:async()=>requests.push(['viz2d',Number(element('viz2d-time').value)]),
  updateViz3dIso:async()=>requests.push(['viz3d',Number(element('viz3d-iso-time').value)])});
 vm.runInContext(source,context);
 const workspace=context.window.ScientificWorkspace;workspace.bind();workspace.onNavigate(kind);workspace.syncFrom(kind);
 return {workspace,requests,timers,frames,
  start(){workspace.togglePlay(kind);},
  delay(){return timers.values().next().value?.delay;},
  advance(ms){now+=ms;},
  async drainFrames(){
   if(stallFrames)return;
   while(frames.size){const [id,callback]=frames.entries().next().value;frames.delete(id);callback(now);await flush();}
  },
  async fireTimer(lateness=0){
   const [id,timer]=timers.entries().next().value||[];assert.ok(timer,'expected a scheduled playback timer');
   timers.delete(id);now+=timer.delay+lateness;timer.fn();await flush();await this.drainFrames();
  },
  stop(){workspace.stop(kind);}
 };
}

for(const kind of ['viz2d','viz3d']){
 test(`${kind}: playback advances sequentially when requestAnimationFrame is throttled`,async()=>{
  const e=env(kind,{stallFrames:true});e.start();await flush();
  assert.deepEqual(e.requests,[[kind,0]],'the initial real frame renders before playback cadence begins');
  await e.fireTimer();
  await e.fireTimer(100);
  await e.fireTimer();
  assert.deepEqual(e.requests,[[kind,0],[kind,1]],
   'a throttled paint callback must not leave the play button active while frames stay frozen');
  assert.equal(e.timers.size>0,true,'playback keeps scheduling the following actual frame');
  e.stop();
 });
}

for(const kind of ['viz2d','viz3d']){
 test(`${kind}: timer lateness is recovered against the accumulated deadline without skipping outputs`,async()=>{
  const e=env(kind),period=1000/12;e.start();await flush();await e.drainFrames();
  assert.deepEqual(e.requests,[[kind,0]]);
  await e.fireTimer(10);
  assert.deepEqual(e.requests,[[kind,0],[kind,1]],'a late timer displays exactly the next output frame');
  assert.ok(Math.abs(e.delay()-(period-10))<0.01,
   'the following wait should recover the 10 ms callback lateness against the original cadence');
  await e.fireTimer();
  assert.deepEqual(e.requests,[[kind,0],[kind,1],[kind,2]],'output frames remain sequential');
  assert.ok(Math.abs(e.delay()-period)<0.01,'cadence returns to one target interval after recovery');
  e.stop();
 });

 test(`${kind}: a severely late timer rebases once instead of bursting catch-up frames`,async()=>{
  const e=env(kind),period=1000/12;e.start();await flush();await e.drainFrames();
  await e.fireTimer(period*3);
  assert.deepEqual(e.requests,[[kind,0],[kind,1]],'lateness advances one output, never skips or queues several');
  assert.ok(Math.abs(e.delay())<0.01,'after a slow render misses its deadline, the next output should start as soon as the previous one completes');
  await e.fireTimer();
  assert.deepEqual(e.requests,[[kind,0],[kind,1],[kind,2]],'the next wake advances only one frame');
  assert.ok(Math.abs(e.delay()-period)<0.01,'the following frame returns to the target cadence');
  e.stop();
 });
}

console.log('scientific playback accumulated-deadline scheduler tests passed');
