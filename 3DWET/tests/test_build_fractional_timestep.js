const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {test}=require('node:test');
const source=fs.readFileSync('3DWET/app/static/js/app.js','utf8');
const body=source.slice(source.indexOf('async function buildCase()'),source.indexOf('// ── Modules ─'));
function environment(value){
 const requests=[],statuses=[];let confirmations=0;
 const context=vm.createContext({state:{activeCase:'Test Lake',engines:[],icData:{}},window:{},
  $:id=>({value:id==='build-dt'?value:'6'}),
  _readModelPeriod:()=>({start:'2020-01-01 00:00:00',stop:'2020-01-01 00:20:00'}),
  confirmStudio:async()=>{confirmations++;return true;},
  api:async(path,options)=>{requests.push({path,body:options.body});return {error:'End probe after request'};},
  _ppStatus:(...args)=>statuses.push(args),toast(){}});
 vm.runInContext(body,context);
 return {context,requests,statuses,confirmations:()=>confirmations};
}
test('build UI sends the exact positive fractional step without integer truncation',async()=>{
 for(const value of ['0.5','1.9060091']){
  const e=environment(value);await e.context.buildCase();
  assert.equal(e.requests[0].body.timestep,Number(value));
 }
});
test('invalid build UI step cannot confirm or send a destructive rebuild request',async()=>{
 for(const value of ['0','-0.1','NaN','Infinity']){
  const e=environment(value);await e.context.buildCase();
  assert.equal(e.requests.length,0);assert.equal(e.confirmations(),0);assert.ok(e.statuses.length);
 }
});
