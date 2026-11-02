const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('3DWET/app/static/js/app.js','utf8');
const requests=[];
class XHR {constructor(){requests.push(this);}open(){}setRequestHeader(){}send(){}abort(){this.aborted=true;this.onabort?.();}}
const context=vm.createContext({XMLHttpRequest:XHR,AbortController,Promise,JSON});
vm.runInContext(source.slice(source.indexOf('async function api('),source.indexOf('// ── Navigation')),context);
(async()=>{
 const abort=new AbortController();const pending=context.api('/old-field',{signal:abort.signal});
 abort.abort();assert.equal(requests[0].aborted,true,'stale field request must be abortable');
 assert.equal((await pending).aborted,true,'aborted request settles without a user-facing network error');
 const already=new AbortController();already.abort();const skip=await context.api('/never-sent',{signal:already.signal});
 assert.equal(skip.aborted,true);
 const normal=context.api('/current-field');const current=requests.at(-1);current.responseText='{"value":0}';current.onload();
 assert.equal((await normal).value,0,'ordinary zero-valued response still works');
 console.log('Result XHR cancellation settles stale requests and preserves ordinary responses PASS');
})().catch(e=>{console.error(e);process.exitCode=1;});
