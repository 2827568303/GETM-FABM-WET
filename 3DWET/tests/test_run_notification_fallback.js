const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const source=fs.readFileSync('3DWET/app/static/js/app.js','utf8');
const template=fs.readFileSync('3DWET/app/templates/index.html','utf8');
assert.match(template,/id="run-notification-center"/,'the global run notification fallback must exist in the shell');
assert.match(template,/id="run-notification-status"/,'the persistent panel must expose live run status and ETA');
assert.match(template,/id="run-notification-list"/,'terminal alerts must remain available in an in-app list');
const start=source.indexOf('function appendRunNotificationFallback(');
const end=source.indexOf('function renderFabmRepairSummary(',start);
assert.ok(start>=0&&end>start,'run notification fallback helpers must be defined beside notifyUser');
class Element {
  constructor(id=''){this.id=id;this.children=[];this.attrs={};this.dataset={};this.textContent='';this.hidden=id==='run-notification-center';this.className='';}
  appendChild(child){this.children.push(child);return child;}
  prepend(child){this.children.unshift(child);return child;}
  remove(){this.removed=true;}
  setAttribute(name,value){this.attrs[name]=String(value);}
}
const elements=new Map();
const get=id=>{if(!elements.has(id))elements.set(id,new Element(id));return elements.get(id);};
const toasts=[];
const notificationApi={permission:'denied'};
const context=vm.createContext({document:{getElementById:get,createElement:tag=>new Element(tag)},window:{Notification:notificationApi},Notification:notificationApi,$:get,fmt:value=>String(value),state:{runPollTimer:null},
  toast:(...args)=>toasts.push(args),ModelDates:{formatText:value=>value},StudioIcons:{node:()=>new Element('icon')},fmt:value=>String(value),console});
vm.runInContext(source.slice(start,end),context);
context.updateRunNotificationStatus({status:'running',progress:42,eta_minutes:1.2,current_step:42,total_steps:100});
assert.equal(get('run-notification-center').hidden,false,'the fallback panel must be visible without notification permission');
assert.match(get('run-notification-status').textContent,/42%/,'the panel retains current progress');
assert.match(get('run-notification-status').textContent,/预计剩余 0小时2分钟/,
  'the panel formats ETA as the displayed remaining-time duration');
context.updateRunNotificationStatus({status:'failed',progress:42,logs:['[ERROR] model crashed']});
assert.equal(get('run-notification-status').dataset.status,'failed','terminal status is available in the persistent panel');
assert.match(get('run-notification-status').textContent,/model crashed/,'the failure summary includes the run log reason');
context.updateRunNotificationStatus({status:'completed',progress:100});
assert.equal(get('run-notification-status').dataset.status,'completed','successful terminal status is also retained');
context.notifyUser('Model finished','Completed 100 steps');
assert.equal(get('run-notification-list').children.length,1,'terminal notification remains in the panel');
assert.match(get('run-notification-list').children[0].children[1].textContent,/Model finished.*Completed 100 steps/);
assert.equal(get('run-notification-center').hidden,false);
assert.equal(toasts.length,1,'existing transient toast may still be shown as an additional cue');
assert.match(context.runFailureReason({logs:['[ERROR] model crashed']}),/model crashed/,'failure reason should come from run logs');
assert.equal(context.window.Notification.permission,'denied','fallback must not change the pending/denied native permission choice');
console.log('run notification fallback: persistent ETA/progress and terminal/failure details without native permission PASS');
