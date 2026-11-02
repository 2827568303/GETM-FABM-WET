'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }
var nt=Process.findModuleByName('ntdll.dll');
['NtWaitForSingleObject','NtWaitForMultipleObjects','NtDelayExecution','NtRemoveIoCompletion','NtUserMessageCall','NtUserWaitMessage'].forEach(function(n){
  var m = Process.findModuleByName('ntdll.dll');
  var p = (m.findExportByName(n) || (Process.findModuleByName('win32u.dll')||{findExportByName:function(){return null}}).findExportByName(n));
  if(!p){ return; }
  Interceptor.attach(p,{onEnter:function(a){ this.t=Date.now(); this.n=n; this.tid=Process.getCurrentThreadId(); },onLeave:function(){
    var dt=Date.now()-this.t;
    if(Date.now()-t0>2000 && dt>1500) emit(this.n+' '+dt+'ms tid='+this.tid+' from '+mod(this.returnAddress));
  }});
});
emit('ready');
