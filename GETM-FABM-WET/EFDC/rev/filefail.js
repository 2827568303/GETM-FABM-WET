'use strict';
function send2(s){ send(s); }
var T0=Date.now(); function t(){ return ((Date.now()-T0)/1000).toFixed(2); }
function wstr(p){ try{ return p.isNull()?'':p.readUtf16String(); }catch(e){ return '?'; } }
function astr(p){ try{ return p.isNull()?'':p.readAnsiString(); }catch(e){ return '?'; } }
setTimeout(function(){
  var k=Process.findModuleByName('kernel32.dll');
  Interceptor.attach(k.findExportByName('CreateFileW'),{
    onEnter:function(a){ this.p=wstr(a[0]); },
    onLeave:function(r){ if(r.toInt32()===-1) send2('['+t()+'] FAIL '+JSON.stringify(this.p)); }
  });
  Interceptor.attach(k.findExportByName('CreateFileA'),{
    onEnter:function(a){ this.p=astr(a[0]); },
    onLeave:function(r){ if(r.toInt32()===-1) send2('['+t()+'] FAIL-A '+JSON.stringify(this.p)); }
  });
  send2('hooked file');
}, 150);
send2('loaded');
