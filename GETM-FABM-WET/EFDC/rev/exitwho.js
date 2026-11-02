'use strict';
function send2(s){ send(s); }
var T0=Date.now(); function t(){ return ((Date.now()-T0)/1000).toFixed(2); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); if(m) return m.name+'+0x'+a.sub(m.base).toString(16);}catch(e){} return String(a); }
setTimeout(function(){
  var k=Process.findModuleByName('kernel32.dll');
  ['ExitProcess','TerminateProcess','ExitThread','RtlExitUserProcess'].forEach(function(fn){
    var p=k.findExportByName(fn); if(!p) return;
    try{ Interceptor.attach(p,{ onEnter:function(a){ send2('['+t()+'] '+fn+' code='+a[0].toInt32()+' from '+mod(this.returnAddress)); } }); send2('hooked '+fn); }catch(e){ send2('fail '+fn); }
  });
  var nt=Process.findModuleByName('ntdll.dll');
  if(nt){ var p=nt.findExportByName('NtTerminateProcess'); if(p){ Interceptor.attach(p,{ onEnter:function(a){ send2('['+t()+'] NtTerminateProcess from '+mod(this.returnAddress)); } }); send2('hooked NtTerminateProcess'); } }
  var u=Process.findModuleByName('user32.dll');
  var pm=u.findExportByName('PostQuitMessage');
  if(pm) Interceptor.attach(pm,{ onEnter:function(a){ send2('['+t()+'] PostQuitMessage '+a[0].toInt32()+' from '+mod(this.returnAddress)); } });
}, 150);
send2('loaded');
