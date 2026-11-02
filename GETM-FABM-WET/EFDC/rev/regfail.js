'use strict';
function send2(s){ send(s); }
var T0=Date.now(); function t(){ return ((Date.now()-T0)/1000).toFixed(2); }
function wstr(p){ try{ return p.isNull()?'':p.readUtf16String(); }catch(e){ return '?'; } }
function astr(p){ try{ return p.isNull()?'':p.readAnsiString(); }catch(e){ return '?'; } }
setTimeout(function(){
  var a=Process.findModuleByName('advapi32.dll');
  Interceptor.attach(a.findExportByName('RegOpenKeyExW'),{
    onEnter:function(x){ this.k=wstr(x[1]); },
    onLeave:function(r){ if((r.toInt32()>>>0)!==0) send2('['+t()+'] RegOpen FAIL 0x'+(r.toInt32()>>>0).toString(16)+' '+JSON.stringify(this.k)); }
  });
  Interceptor.attach(a.findExportByName('RegOpenKeyExA'),{
    onEnter:function(x){ this.k=astr(x[1]); },
    onLeave:function(r){ if((r.toInt32()>>>0)!==0) send2('['+t()+'] RegOpenA FAIL 0x'+(r.toInt32()>>>0).toString(16)+' '+JSON.stringify(this.k)); }
  });
  Interceptor.attach(a.findExportByName('RegQueryValueExW'),{
    onEnter:function(x){ this.n=wstr(x[1]); },
    onLeave:function(r){ if((r.toInt32()>>>0)!==0) send2('['+t()+'] RegQueryW FAIL 0x'+(r.toInt32()>>>0).toString(16)+' '+JSON.stringify(this.n)); }
  });
  Interceptor.attach(a.findExportByName('RegQueryValueExA'),{
    onEnter:function(x){ this.n=astr(x[1]); },
    onLeave:function(r){ if((r.toInt32()>>>0)!==0) send2('['+t()+'] RegQueryA FAIL 0x'+(r.toInt32()>>>0).toString(16)+' '+JSON.stringify(this.n)); }
  });
  send2('hooked registry');
}, 150);
send2('loaded');
