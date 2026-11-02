'use strict';
function send2(s){ send(s); }
function astr(p){ try{ return p.isNull()?'':p.readAnsiString(); }catch(e){ return '?'; } }
var T0=Date.now(); function t(){ return ((Date.now()-T0)/1000).toFixed(2); }
setTimeout(function(){
  var u=Process.findModuleByName('user32.dll');
  Interceptor.attach(u.findExportByName('CreateWindowExA'),{
    onEnter:function(a){ this.c=astr(a[1]); this.n=astr(a[2]); },
    onLeave:function(r){ send2('['+t()+'] CW cls='+JSON.stringify(this.c)+' name='+JSON.stringify(this.n)+' hwnd='+r); }
  });
  Interceptor.attach(u.findExportByName('DestroyWindow'),{
    onEnter:function(a){ send2('['+t()+'] DestroyWindow '+a[0]); }
  });
  var mb=Process.findModuleByName('msvbvm60.dll');
  Interceptor.attach(mb.findExportByName('rtcMsgBox'),{ onEnter:function(){ send2('['+t()+'] rtcMsgBox'); } });
  send2('hooked');
}, 200);
send2('loaded');

