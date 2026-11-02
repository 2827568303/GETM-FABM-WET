'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }
function ftrace(ctx,n){ try{ return Thread.backtrace(ctx, Backtracer.FUZZY).slice(0,n||14).map(mod).join(' <- '); }catch(e){ return '?'; } }
['MsgWaitForMultipleObjects','MsgWaitForMultipleObjectsEx'].forEach(function(n){
  var u32=Process.findModuleByName('user32.dll');
  var p=u32.findExportByName(n);
  if(!p) return;
  Interceptor.attach(p,{onEnter:function(a){ this.t=Date.now(); this.chain=ftrace(this.context,14); },
    onLeave:function(){ var dt=Date.now()-this.t; if(dt>2000) emit(n+' '+dt+'ms  '+this.chain); }});
});
emit('ready');
