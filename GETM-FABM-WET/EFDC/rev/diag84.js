'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }
var vb=Process.findModuleByName('MSVBVM60.DLL');
var target=vb.base.add(0x2ad05);
emit('target '+target);
Interceptor.attach(target,{onEnter:function(){
  emit('VB End called tid='+Process.getCurrentThreadId());
  try{ emit('  '+Thread.backtrace(this.context, Backtracer.FUZZY).slice(0,24).map(mod).join(' <- ')); }catch(e){}
}});
emit('ready');
