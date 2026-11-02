'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }
var k32=Process.findModuleByName('kernel32.dll');
Interceptor.attach(k32.findExportByName('RaiseException'),{onEnter:function(a){
  var t=Date.now()-t0; if(t<3000) return;
  var code=a[0].toUInt32()>>>0;
  emit('RAISE code=0x'+code.toString(16)+' from '+mod(this.returnAddress));
  try{ emit('   '+Thread.backtrace(this.context, Backtracer.FUZZY).slice(0,18).map(mod).join(' <- ')); }catch(e){}
}});
emit('ready');
