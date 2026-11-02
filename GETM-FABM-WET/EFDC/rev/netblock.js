'use strict';
function send2(s){ send(s); }
var T0=Date.now(); function t(){ return ((Date.now()-T0)/1000).toFixed(2); }
var done={};
function tryHook(mod,fn,cb){ var k=mod+'!'+fn; if(done[k]) return; var m=Process.findModuleByName(mod); if(!m) return; var p=m.findExportByName(fn); if(!p) return;
  try{ Interceptor.attach(p,cb); done[k]=1; send2('hooked '+k); }catch(e){ done[k]=1; } }
var iv=setInterval(function(){
  tryHook('winhttp.dll','WinHttpConnect',{
    onEnter:function(a){ send2('['+t()+'] WinHttpConnect '+a[1]+' -> BLOCKED'); },
    onLeave:function(r){ }
  });
}, 200);
setTimeout(function(){ clearInterval(iv); }, 12000);
send2('loaded');
