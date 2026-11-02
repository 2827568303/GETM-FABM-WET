'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }
var u32=Process.findModuleByName('user32.dll');
['SetTimer','KillTimer'].forEach(function(n){
  var p=u32.findExportByName(n);
  Interceptor.attach(p,{onEnter:function(a){
    emit(n+' hwnd='+a[0]+' id='+a[1]+' ms='+(n==='SetTimer'?a[2].toInt32():'-')+' cb='+(n==='SetTimer'?a[3]:'-')+' from '+mod(this.returnAddress));
  }});
});
var vb=Process.findModuleByName('MSVBVM60.DLL');
emit('ready');
