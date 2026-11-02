'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
var u32=Process.findModuleByName('user32.dll');
var n=0;
Interceptor.attach(u32.findExportByName('CreateWindowExW'),{onEnter:function(a){
  n++;
  if(n<=40){ try{ emit('CW '+a[1].readUtf16String()); }catch(e){ emit('CW <atom?>'); } }
}});
Interceptor.attach(u32.findExportByName('CreateWindowExA'),{onEnter:function(a){
  n++;
  if(n<=40){ try{ emit('CWA '+a[1].readAnsiString()); }catch(e){ emit('CWA <atom?>'); } }
}});
emit('ready');
