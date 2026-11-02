'use strict';
function send2(s){ send(s); }
var T0=Date.now(); function t(){ return ((Date.now()-T0)/1000).toFixed(2); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); if(m) return m.name+'+0x'+a.sub(m.base).toString(16);}catch(e){} return String(a); }
setTimeout(function(){
  var mb=Process.findModuleByName('msvbvm60.dll');
  Interceptor.attach(mb.findExportByName('__vbaEnd'),{ onEnter:function(){ send2('['+t()+'] __vbaEnd from '+mod(this.returnAddress)); } });
  Interceptor.attach(mb.findExportByName('__vbaExitProc'),{ onEnter:function(){ send2('['+t()+'] __vbaExitProc from '+mod(this.returnAddress)); } });
  var u=Process.findModuleByName('user32.dll');
  Interceptor.attach(u.findExportByName('PostQuitMessage'),{ onEnter:function(a){ send2('['+t()+'] PostQuitMessage '+a[0]); } });
  send2('hooked');
}, 250);
send2('loaded');
