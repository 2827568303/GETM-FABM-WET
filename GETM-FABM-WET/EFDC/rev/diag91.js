'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }
var w32u=Process.findModuleByName('win32u.dll');
['NtUserWaitMessage','NtUserGetMessage','NtUserPeekMessage'].forEach(function(n){
  var p=w32u.findExportByName(n); if(!p){ emit('no '+n); return; }
  Interceptor.attach(p,{onEnter:function(){ this.t=Date.now(); this.n=n; },onLeave:function(){
    var dt=Date.now()-this.t;
    if(Date.now()-t0>2000 && dt>200) emit(this.n+' '+dt+'ms from '+mod(this.returnAddress));
  }});
});
var u32=Process.findModuleByName('user32.dll');
var cnt=0;
['PeekMessageW','GetMessageW'].forEach(function(n){
  var p=u32.findExportByName(n);
  if(p) Interceptor.attach(p,{onEnter:function(){ cnt++; }});
});
setTimeout(function(){ emit('Peek/GetMessage count='+cnt); }, 9000);
emit('ready');
