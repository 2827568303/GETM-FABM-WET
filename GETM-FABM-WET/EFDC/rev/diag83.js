'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }
var nt=Process.findModuleByName('ntdll.dll');
Interceptor.attach(nt.findExportByName('RtlExitUserProcess'),{onEnter:function(a){
  emit('RtlExitUserProcess('+a[0].toInt32()+') tid='+Process.getCurrentThreadId()+' from '+mod(this.returnAddress));
  try{ emit('  '+Thread.backtrace(this.context, Backtracer.FUZZY).slice(0,20).map(mod).join(' <- ')); }catch(e){}
}});
var k32=Process.findModuleByName('kernel32.dll');
Interceptor.attach(k32.findExportByName('ExitProcess'),{onEnter:function(a){
  emit('ExitProcess('+a[0].toInt32()+') tid='+Process.getCurrentThreadId()+' from '+mod(this.returnAddress));
}});
emit('ready');
