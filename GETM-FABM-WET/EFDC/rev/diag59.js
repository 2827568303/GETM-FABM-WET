'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
var u32=Process.findModuleByName('user32.dll');
Interceptor.attach(u32.findExportByName('CreateWindowExW'),{onEnter:function(a){
  try{ var c=a[1].readUtf16String(); if(/Thunder/.test(c)) emit('Create '+c); }catch(e){}
}});
emit('ready');
