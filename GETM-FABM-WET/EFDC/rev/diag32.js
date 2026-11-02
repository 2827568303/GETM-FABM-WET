'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }
var nt=Process.findModuleByName('ntdll.dll');
Interceptor.attach(nt.findExportByName('RtlExitUserProcess'), { onEnter: function(a){
  emit('RtlExitUserProcess from ' + mod(this.returnAddress));
  try{ emit('ACC: ' + Thread.backtrace(this.context, Backtracer.ACCURATE).slice(0,20).map(mod).join(' <- ')); }catch(e){ emit('acc err '+e); }
  try{ emit('FUZ: ' + Thread.backtrace(this.context, Backtracer.FUZZY).slice(0,26).map(mod).join(' <- ')); }catch(e){ emit('fuz err '+e); }
}});
var u32=Process.findModuleByName('user32.dll');
Interceptor.replace(u32.findExportByName('SoftModalMessageBox'), new NativeCallback(function(){ return 1; },'int',['pointer']));
emit('ready');
