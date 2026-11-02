'use strict';
function send2(s){ send(s); }
function wstr(p){ try{ return p.isNull()?'':p.readUtf16String(); }catch(e){ return '?'; } }
setTimeout(function(){
  var k=Process.findModuleByName('kernel32.dll');
  Interceptor.attach(k.findExportByName('CreateFileW'),{
    onEnter:function(a){ this.p=wstr(a[0]); },
    onLeave:function(r){ send2('open '+(r.toInt32()===-1?'FAIL':'ok')+' '+JSON.stringify(this.p)); }
  });
  var adv=Process.findModuleByName('advapi32.dll');
  var regopen=adv.findExportByName('RegOpenKeyExW');
  Interceptor.attach(regopen,{ onEnter:function(a){ send2('regopen '+JSON.stringify(wstr(a[1]))); } });
  send2('hooked');
}, 150);
send2('loaded');
