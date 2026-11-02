'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
var vb = Process.findModuleByName('MSVBVM60.DLL');
Interceptor.attach(vb.findExportByName('__vbaFileOpen'), { onEnter: function(a){
  var p=''; try{ p=a[3].readUtf16String(); }catch(e){}
  emit('OPEN['+a[0].toString()+'] '+p);
}});
var u32=Process.findModuleByName('user32.dll');
Interceptor.attach(u32.findExportByName('SoftModalMessageBox'),{onEnter:function(){ emit('=== MSGBOX ==='); }});
emit('ready');
