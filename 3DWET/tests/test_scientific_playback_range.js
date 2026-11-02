const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {test}=require('node:test');
const source=fs.readFileSync('3DWET/app/static/js/scientific_workspace.js','utf8');
const flush=()=>new Promise(resolve=>setImmediate(resolve));
function env(kind='viz2d',count=6,realTimers=false){
 const nodes=new Map(),timers=new Map(),requests=[],events={};let timerId=0,frameId=0,hold=null,fail=false,renderHook=null,wallOffset=0,monoOffset=0;
 function element(id){
  if(!nodes.has(id))nodes.set(id,{id,value:'',textContent:'',dataset:{},style:{},options:[],handlers:{},replaceChildren(){},
   setAttribute(k,v){this[k]=String(v);},removeAttribute(k){delete this[k];},
   addEventListener(k,fn){(this.handlers[k]??=[]).push(fn);},
   dispatch(k){for(const fn of this.handlers[k]||[])fn({target:this});},
   classList:{toggle(){return false;},remove(){},contains(){return false;}}});
  return nodes.get(id);
 }
 const state={activeCasePath:'A',caseRevision:1,variables3d:[{name:'temp',time_axis:'volume',ntimesteps:count}],
  variables2d:[{name:'flux',time_axis:'surface',ntimesteps:3}],
  resultTimeAxes:{volume:Array.from({length:count},(_,n)=>`2026-DOY288 ${String(n).padStart(2,'0')}:00:00`),surface:['s0','s1','s2']},
  timeLabels:Array.from({length:40},(_,n)=>'wrong'+n)};
 for(const k of ['viz2d','viz3d']){
  element(k==='viz2d'?'viz2d-var':'viz3d-iso-var').value='temp';
  element(k==='viz2d'?'viz2d-time':'viz3d-iso-time').value='0';element(k+'-time-slider').value='0';
  element(k+'-speed').value='1';element(k+'-play-start').value='0';element(k+'-play-end').value=String(Math.max(0,count-1));
 }
 element('viz3d-iso-render').value='cloud';element('viz3d-iso-overlay').checked=true;
 let w;
 async function render(k){
  const frame=Number(element(k==='viz2d'?'viz2d-time':'viz3d-iso-time').value);requests.push([k,frame]);
  if(hold){const promise=hold.promise;hold=null;await promise;}
  if(fail){w.failure(k,'controlled render failure');return;}
  renderHook?.(k,frame);
 }
 const RealDate=Date;class WallDate extends RealDate{static now(){return RealDate.now()+wallOffset;}}
 const monoClock={now:()=>RealDate.now()+monoOffset};
 const context=vm.createContext({window:{performance:monoClock,StudioIcons:{node:()=>({})},requestAnimationFrame:callback=>{const id=++frameId;queueMicrotask(()=>callback(monoClock.now()));return id;},cancelAnimationFrame(){}},state,console,Date:WallDate,performance:monoClock,document:{readyState:'loading',hidden:false,getElementById:element,
  addEventListener:(k,fn)=>events[k]=fn,querySelectorAll:()=>[]},ModelDates:{format:v=>v},
  setTimeout:(fn,delay=0)=>{const id=++timerId;timers.set(id,{fn,delay});if(realTimers)timers.get(id).native=setTimeout(()=>{timers.delete(id);fn();},delay);return id;},
  clearTimeout:id=>{const timer=timers.get(id);if(timer?.native)clearTimeout(timer.native);timers.delete(id);},
  updateViz2d:()=>render('viz2d'),updateViz3dIso:()=>render('viz3d')});
 vm.runInContext(source,context);w=context.window.ScientificWorkspace;w.bind();w.onNavigate(kind);w.syncFrom(kind);
 function range(start,end){element(kind+'-play-start').value=String(start);element(kind+'-play-end').value=String(end);element(kind+'-play-end').dispatch('input');}
 function block(){let release;const promise=new Promise(resolve=>release=resolve);hold={promise};return release;}
 return {w,kind,state,element,requests,timers,events,context,range,block,fail:v=>fail=v,onRender:fn=>renderHook=fn,
  frame:()=>Number(element(kind==='viz2d'?'viz2d-time':'viz3d-iso-time').value),
  setFrame:n=>element(kind==='viz2d'?'viz2d-time':'viz3d-iso-time').value=String(n),
  tick:async()=>{const entry=timers.entries().next().value;if(!entry)return;timers.delete(entry[0]);monoOffset+=entry[1].delay;entry[1].fn();await flush();},
  nextDelay:()=>timers.values().next().value?.delay,jumpWallClock:ms=>{wallOffset+=ms;},advanceMono:ms=>{monoOffset+=ms;}};
}

for(const kind of ['viz2d','viz3d']){
 test(`${kind}: wall-clock jumps cannot turn a 1 fps target into rapid catch-up frames`,async()=>{
  const e=env(kind,12,true);e.range(0,10);e.onRender(()=>e.jumpWallClock(6507));e.w.togglePlay(kind);await flush();
  await new Promise(resolve=>setTimeout(resolve,120));
  assert.equal(e.frame(),0,'a wall-clock jump must not consume the 1000 ms monotonic frame interval');
  e.w.stop(kind);
 });
 test(`${kind}: an overlong render advances at most one frame before scheduling again`,async()=>{
  const e=env(kind,12);e.range(0,10);e.onRender(()=>e.advanceMono(6507));e.w.togglePlay(kind);await flush();
  assert.equal(e.frame(),0);assert.equal(e.timers.size,1,'one timer is scheduled after the long render');
  await e.tick();assert.equal(e.frame(),1,'one timer can advance only one frame');
  assert.equal(e.requests.length,2,'no catch-up frames are queued');
  e.w.stop(kind);
 });
 test(`${kind}: real timers cannot advance six frames in one second at 1 fps`,async()=>{
  const e=env(kind,12,true);e.range(0,10);e.w.togglePlay(kind);await flush();
  const started=Date.now();await new Promise(resolve=>setTimeout(resolve,1100));
  const elapsed=Date.now()-started;assert.ok(elapsed>=1000);assert.ok(elapsed<1600);
  assert.ok(e.frame()<=1,`only frame 1 may be reached after ${elapsed} ms at 1 fps (actual ${e.frame()})`);
  e.w.stop(kind);
 });
 test(`${kind}: playback timer uses milliseconds per target frame and never schedules catch-up frames`,async()=>{
  const e=env(kind);e.range(0,4);
  for(const [speed,interval] of [['0.5',2000],['1',1000],['2',500],['4',250],['8',125],['12',1000/12]]){
   e.element(kind+'-speed').value=speed;e.w.togglePlay(kind);await flush();
   assert.ok(Math.abs(e.nextDelay()-interval)<=5,`${speed} fps must schedule approximately ${interval} ms`);
   e.w.stop(kind);
  }
  const slow=env(kind);slow.range(0,4);slow.element(kind+'-speed').value='1';const release=slow.block();slow.onRender(()=>slow.advanceMono(250));slow.w.togglePlay(kind);await flush();
  assert.deepEqual(slow.requests,[[kind,0]]);assert.equal(slow.timers.size,0,'a frame in flight must not have a second timer');
  release();await flush();assert.ok(Math.abs(slow.nextDelay()-750)<=5,'render time counts toward the target frame interval');
  slow.w.stop(kind);
 });
 test(`${kind}: bounded playback renders both endpoints and stops after the last render`,async()=>{
  const e=env(kind);e.range(2,4);e.w.togglePlay(kind);await flush();
  assert.deepEqual(e.requests,[[kind,2]],'the selected first frame is rendered before advancing');
  await e.tick();await e.tick();assert.deepEqual(e.requests,[[kind,2],[kind,3],[kind,4]]);
  assert.equal(e.timers.size,0);assert.equal(e.frame(),4);
  assert.match(e.element(kind+'-play-start-label').textContent,/02:00:00/);
  assert.match(e.element(kind+'-play-end-label').textContent,/04:00:00/);
 });
 test(`${kind}: slow first and last frames cannot be skipped or overlap`,async()=>{
  const e=env(kind);e.range(1,2);const release=e.block();e.w.togglePlay(kind);
  await e.tick();assert.deepEqual(e.requests,[[kind,1]]);release();await flush();
  const releaseLast=e.block(),last=e.tick();await e.tick();assert.equal(e.timers.size,0,'no timer is queued while a slow frame is rendering');
  assert.deepEqual(e.requests,[[kind,1],[kind,2]]);releaseLast();await last;assert.equal(e.timers.size,0);
 });
 test(`${kind}: single-frame range renders exactly once`,async()=>{
  const e=env(kind);e.range(3,3);e.w.togglePlay(kind);await flush();
  assert.deepEqual(e.requests,[[kind,3]]);assert.equal(e.timers.size,0);
 });
 test(`${kind}: pause resumes inside the range and completed playback restarts at its start`,async()=>{
  const e=env(kind);e.range(1,4);e.w.togglePlay(kind);await flush();await e.tick();
  e.w.togglePlay(kind);assert.equal(e.timers.size,0);e.w.togglePlay(kind);await flush();
  assert.equal(e.frame(),2);assert.deepEqual(e.requests,[[kind,1],[kind,2]],'resume must not render the paused frame again');
  await e.tick();assert.equal(e.frame(),3);await e.tick();assert.equal(e.timers.size,0);
  e.w.togglePlay(kind);await flush();assert.equal(e.frame(),1);e.w.stop();
 });
 test(`${kind}: starting playback inside the selected range starts at the current frame`,async()=>{
  const e=env(kind);e.setFrame(3);e.range(1,4);e.w.togglePlay(kind);await flush();
  assert.deepEqual(e.requests,[[kind,3]]);e.w.stop();
 });
 test(`${kind}: starting playback before the range or at its end starts at the range beginning`,async()=>{
  for(const frame of [0,4]){
   const e=env(kind);e.setFrame(frame);e.range(1,4);e.w.togglePlay(kind);await flush();
   assert.deepEqual(e.requests,[[kind,1]],`frame ${frame}`);e.w.stop();
  }
 });
 test(`${kind}: continuous mouse input stops playback and refreshes every latest selection`,async()=>{
  const e=env(kind);e.w.togglePlay(kind);await flush();const before=e.requests.length;
  const slider=e.element(kind==='viz2d'?'viz2d-time':'viz3d-time-slider');
  for(const n of [0,3,1]){slider.value=String(n);slider.dispatch('input');}
  await flush();assert.equal(e.timers.size,0);assert.equal(e.frame(),1);
  assert.deepEqual(e.requests.slice(before),[[kind,0],[kind,3],[kind,1]],'no change event or mouse release is needed');
 });
 test(`${kind}: authoritative frame counts without date labels still support a stable range`,async()=>{
  const e=env(kind);e.state.resultTimeAxes={};delete e.state.timeLabels;e.w.updateTimeControls(kind);e.range(1,2);
  e.w.togglePlay(kind);await flush();assert.deepEqual(e.requests,[[kind,1]]);await e.tick();
  assert.deepEqual(e.requests,[[kind,1],[kind,2]]);assert.equal(e.timers.size,0);
  assert.equal(e.element(kind+'-play-start-label').textContent,'帧 1');
 });
 test(`${kind}: invalid endpoint drafts cannot fall back to the previous valid range`,async()=>{
  const e=env(kind);e.range(1,4);
  for(const [start,end] of [['',4],[1,''],[1.5,4],[-1,4],[1,6],[4,2],['NaN',4],['Infinity',4]]){
   e.range(start,end);const before=e.requests.length;e.w.togglePlay(kind);await flush();
   assert.equal(e.timers.size,0,`${start}..${end}`);assert.equal(e.requests.length,before);
   assert.ok(e.element(kind+'-play-range-status').textContent.length,'invalid draft must remain visible');
  }
  e.range(2,3);assert.equal(e.element(kind+'-play-range-status').textContent,'');e.w.togglePlay(kind);await flush();
  assert.equal(e.frame(),2);e.w.stop();
 });
 test(`${kind}: a failed first or subsequent render stops instead of skipping to another frame`,async()=>{
  const e=env(kind);e.range(1,4);e.fail(true);e.w.togglePlay(kind);await flush();assert.equal(e.timers.size,0);
  assert.deepEqual(e.requests,[[kind,1]]);e.fail(false);e.w.togglePlay(kind);await flush();
  e.fail(true);await e.tick();assert.equal(e.timers.size,0);assert.equal(e.frame(),2);
 });
 test(`${kind}: old pending ticks cannot stop a restarted generation`,async()=>{
  const e=env(kind);e.range(0,2);e.w.togglePlay(kind);await flush();await e.tick();
  const release=e.block(),oldTick=e.tick();e.w.stop(kind);e.range(0,5);e.w.togglePlay(kind);await flush();
  release();await oldTick;await flush();await flush();const newTimer=[...e.timers].find(([,timer])=>timer.delay>50)?.[0];
  assert.equal(e.timers.size,1);assert.ok(e.timers.has(newTimer));await e.tick();assert.equal(e.frame(),2);e.w.stop();
 });
 test(`${kind}: speed restart and pending initial render keep only the latest generation`,async()=>{
  const e=env(kind);e.range(1,5);const release=e.block();e.w.togglePlay(kind);
  e.element(kind+'-speed').value='4';e.element(kind+'-speed').dispatch('change');await flush();
  const timer=[...e.timers.keys()][0];release();await flush();assert.equal(e.timers.size,1);assert.ok(e.timers.has(timer));
  await e.tick();assert.equal(e.frame(),2);e.w.stop();
 });
 test(`${kind}: variable and case changes stop old playback and use their own actual source axes`,async()=>{
  const e=env(kind);e.range(2,5);e.w.togglePlay(kind);await flush();
  e.element(kind==='viz2d'?'viz2d-var':'viz3d-iso-var').value='flux';e.w.syncFrom(kind);
  assert.equal(e.timers.size,0);assert.equal(e.element(kind+'-play-start').value,'0');assert.equal(e.element(kind+'-play-end').value,'2');
  assert.equal(e.element(kind+'-play-end-label').textContent,'s2');
  e.range(1,4);assert.equal(e.element(kind+'-play-end')['aria-invalid'],'true');
  e.range(1,2);e.state.activeCasePath='B';e.state.caseRevision++;e.w.onNavigate(kind);e.w.updateTimeControls(kind);
  assert.equal(e.element(kind+'-play-start').value,'0');assert.equal(e.element(kind+'-play-end').value,'2');
  e.range(1,4);e.state.caseRevision++;e.w.onNavigate(kind);e.w.updateTimeControls(kind);
  assert.equal(e.element(kind+'-play-start')['aria-invalid'],'false');assert.equal(e.element(kind+'-play-end')['aria-invalid'],'false');
 });
 test(`${kind}: changed inventory counts invalidate running ranges without inventing frames`,async()=>{
  const e=env(kind);e.range(3,5);e.w.togglePlay(kind);await flush();e.state.variables3d[0].ntimesteps=2;e.w.updateTimeControls(kind);
  assert.equal(e.timers.size,0);assert.equal(e.element(kind+'-play-end').value,'1');assert.equal(e.frame(),1);
 });
 test(`${kind}: hidden document and navigation retire pending playback`,async()=>{
  const e=env(kind);const release=e.block();e.w.togglePlay(kind);e.context.document.hidden=true;e.events.visibilitychange();
  release();await flush();assert.equal(e.timers.size,0);e.context.document.hidden=false;
  e.w.togglePlay(kind);await flush();e.w.onNavigate('dashboard');assert.equal(e.timers.size,0);
 });
}
test('starting playback preserves a saved locked range',async()=>{
 const e=env();vm.runInContext(fs.readFileSync('3DWET/app/static/js/scientific_style.js','utf8'),e.context);
 const style=e.context.window.ScientificStyle;e.setFrame(5);
 e.w.publish('viz2d',{variable:'temp',time:5,min:50,max:51,range:style.resolve({caseKey:'A',variable:'temp',min:50,max:51})});
 style.set('A','temp',{mode:'locked'});style.resolve({caseKey:'A',variable:'temp',min:50,max:51});
 e.range(2,4);e.w.togglePlay('viz2d');await flush();assert.equal(style.get('A','temp').mode,'locked');
 assert.equal(style.get('A','temp').min,50);assert.equal(style.get('A','temp').max,51);
 e.w.stop();
});
test('starting auto playback leaves the variable in per-frame automatic mode',async()=>{
 const e=env('viz2d');let setting={mode:'auto',palette:'lake'};
 e.context.window.ScientificStyle={get:()=>({...setting}),set:(key,variable,patch)=>{setting={...setting,...patch};},resolve:options=>({...options,...setting})};
 e.range(1,3);e.w.togglePlay('viz2d');await flush();
 assert.equal(setting.mode,'auto');e.w.stop('viz2d');
});
test('3D range modes use frame bounds for auto and explicit bounds for locked/custom',()=>{
 const e=env('viz3d');vm.runInContext(fs.readFileSync('3DWET/app/static/js/viz3d.js','utf8'),e.context);
 let mode='auto',saved={min:null,max:null},seen;
 e.context.window.ScientificStyle={resolve:options=>{
  seen=options;return {...options,mode,min:mode==='auto'?options.min:saved.min,max:mode==='auto'?options.max:saved.max};
 }};
 const request={key:'A',section:false,opts:{}},data={min:15.17,max:15.18};
 let style=e.context.viz3dStyle(data,'temp',request);
 assert.deepEqual({...seen},{caseKey:'A',variable:'temp',min:15.17,max:15.18});
 assert.equal(style.min,15.17);assert.equal(style.max,15.18);
 mode='locked';saved={min:10,max:20};style=e.context.viz3dStyle(data,'temp',request);
 assert.equal(style.min,10);assert.equal(style.max,20);
 mode='custom';saved={min:15,max:16};style=e.context.viz3dStyle(data,'temp',request);
 assert.equal(style.min,15);assert.equal(style.max,16);
});
test('static terrain cannot display model dates as animation endpoints',()=>{
 const e=env('viz3d');e.element('viz3d-iso-render').value='waterbody';e.element('viz3d-iso-overlay').checked=false;e.w.syncFrom('viz3d');
 for(const edge of ['start','end']){assert.equal(e.element('viz3d-play-'+edge).disabled,true);assert.match(e.element('viz3d-play-'+edge+'-label').textContent,/地形|terrain/i);}
 assert.match(e.element('viz3d-iso-time-label').textContent,/地形|terrain/i);
});
test('the 3D number input renders on input and does not render again on change',async()=>{
 const e=env('viz3d');e.element('viz3d-iso-time').value='3';e.element('viz3d-iso-time').dispatch('input');
 e.element('viz3d-iso-time').dispatch('change');await flush();assert.deepEqual(e.requests,[['viz3d',3]]);
});

test('static terrain round-trip preserves selected result frame and bounded playback range',()=>{
 const e=env('viz3d');e.setFrame(5);e.range(2,5);e.w.syncFrom('viz3d');
 e.element('viz3d-iso-render').value='waterbody';e.element('viz3d-iso-overlay').checked=false;e.w.syncFrom('viz3d');
 e.w.publish('viz3d',{variable:'__bathy__',level:null});
 assert.equal(e.frame(),5,'disabled static controls retain the selected result frame');
 assert.equal(e.element('viz3d-play-start').value,'2');assert.equal(e.element('viz3d-play-end').value,'5');
 e.element('viz3d-iso-overlay').checked=true;e.w.syncFrom('viz3d');
 assert.equal(e.frame(),5);assert.equal(e.element('viz3d-play-start').value,'2');assert.equal(e.element('viz3d-play-end').value,'5');
});
test('empty and one-frame authoritative sources do not borrow the longer global axis',async()=>{
 for(const kind of ['viz2d','viz3d']){
  const empty=env(kind,0);empty.w.togglePlay(kind);await flush();assert.equal(empty.requests.length,0);assert.equal(empty.timers.size,0);
  const single=env(kind,1);single.w.togglePlay(kind);await flush();assert.deepEqual(single.requests,[[kind,0]]);assert.equal(single.timers.size,0);
 }
});
test('both responsive timelines expose labelled endpoints and continuous input binding is owned once',()=>{
 const html=fs.readFileSync('3DWET/app/templates/index.html','utf8'),css=fs.readFileSync('3DWET/app/static/css/scientific_workspace.css','utf8');
 for(const kind of ['viz2d','viz3d'])for(const edge of ['start','end']){
  assert.match(html,new RegExp(`for="${kind}-play-${edge}"`));
  const tag=html.match(new RegExp(`<input[^>]*id="${kind}-play-${edge}"[^>]*>`))?.[0];assert.ok(tag);
  for(const attr of ['type="number"','min="0"','step="1"'])assert.ok(tag.includes(attr));
  assert.ok(html.includes(`id="${kind}-play-${edge}-label"`));
 }
 assert.doesNotMatch(html.match(/<input[^>]*id="viz2d-time"[^>]*>/)[0],/oninput/,'one production binding must prevent duplicate requests');
 assert.doesNotMatch(html.match(/<input[^>]*id="viz3d-iso-time"[^>]*>/)[0],/onchange|oninput/,'3D number input must not request a second render on blur');
 assert.match(css,/sw-play-range/);assert.match(css,/minmax\(0,\s*1fr\)/);
});

test('2D and 3D auto range labels describe per-frame scaling in both built-in locales',()=>{
 const html=fs.readFileSync('3DWET/app/templates/index.html','utf8');
 const en=JSON.parse(fs.readFileSync('3DWET/app/static/i18n/en.json','utf8')).messages;
 const guide=fs.readFileSync('3DWET/docs/USER_GUIDE.md','utf8');
 const option='当前帧自动（逐帧缩放）';
 const hint='自动范围按当前显示帧的有效值更新；播放时每帧重新缩放。不同帧颜色不宜直接作定量比较。跨帧比较可选择“锁定范围”或“自定义范围”。2D/3D相同变量共用范围设置。';
 assert.equal(en[option],'Automatic per frame');
 assert.equal(en[hint],'The range follows valid values in the displayed frame and rescales on every playback frame. Colours should not be compared quantitatively across frames. Choose Locked range or Custom range for cross-frame comparison. 2D and 3D share settings for the same variable.');
 assert.match(guide,/“自动”色标按当前显示帧的有效值缩放/);
 for(const kind of ['viz2d','viz3d']){
  const select=html.match(new RegExp(`<select id="${kind}-range-mode">([\\s\\S]*?)</select>`))?.[1];
  assert.ok(select,`${kind} range selector exists`);
  assert.ok(select.includes(`<option value="auto">${option}</option>`),`${kind} labels frame-wise auto scaling`);
  const rangeStart=html.indexOf(`<select id="${kind}-range-mode">`);
  const hintStart=html.indexOf('<div class="form-hint">',rangeStart);
  const hintEnd=html.indexOf('</div>',hintStart);
  const hintText=html.slice(hintStart,hintEnd);
  assert.ok(hintText.includes(hint),`${kind} explains frame-wise auto scaling`);
  assert.doesNotMatch(hintText,/固定色标|播放期间保持不变|起止帧扫描一次/);
 }
});
