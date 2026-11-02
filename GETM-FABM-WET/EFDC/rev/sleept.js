'use strict';
function send2(s){ send(s); }
var T0=Date.now(); function t(){ return ((Date.now()-T0)/1000).toFixed(2); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); if(m) return m.name+'+0x'+a.sub(m.base).toString(16);}catch(e){} return String(a); }
setTimeout(function(){
  var k=Process.findModuleByName('kernel32.dll');
  Interceptor.attach(k.findExportByName('Sleep'),{
    onEnter:function(a){ this.ms=a[0].toInt32(); },
    onLeave:function(){ if(this.ms>=500) send2('['+t()+'] Sleep('+this.ms+') from '+mod(this.returnAddress)); }
  });
  send2('hooked Sleep');
}, 250);
send2('loaded');
