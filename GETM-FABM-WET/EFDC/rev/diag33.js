'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
var k32=Process.findModuleByName('kernel32.dll');
Interceptor.attach(k32.findExportByName('CreateFileW'),{onEnter:function(a){
  var t=Date.now()-t0;
  if(t<2500) return;
  try{ var f=a[0].readUtf16String(); emit('OPEN '+f); }catch(e){}
}});
var u32=Process.findModuleByName('user32.dll');
Interceptor.replace(u32.findExportByName('SoftModalMessageBox'), new NativeCallback(function(){ return 1; },'int',['pointer']));
emit('ready');
