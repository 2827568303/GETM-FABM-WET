'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
var k32=Process.findModuleByName('kernel32.dll');
Interceptor.attach(k32.findExportByName('CreateFileW'),{onEnter:function(a){
  try{ var f=a[0].readUtf16String(); if(/DSILIC/i.test(f)) emit('OPEN '+f); }catch(e){}
}});
var m=Process.findModuleByName('clr.dll');
if(m){ var p=m.findExportByName('LoadLibraryShim'); }
emit('ready');
