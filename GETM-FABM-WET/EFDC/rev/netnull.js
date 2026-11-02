'use strict';
function send2(s){ send(s); }
var T0=Date.now(); function t(){ return ((Date.now()-T0)/1000).toFixed(2); }
var done=false;
var iv=setInterval(function(){
  if(done) return;
  var m=Process.findModuleByName('winhttp.dll'); if(!m) return;
  var p=m.findExportByName('WinHttpConnect'); if(!p) return;
  done=true; clearInterval(iv);
  Interceptor.attach(p,{ onLeave:function(r){ send2('['+t()+'] WinHttpConnect -> NULL'); r.replace(ptr(0)); } });
  send2('hooked WinHttpConnect (always NULL)');
}, 200);
setTimeout(function(){ clearInterval(iv); }, 14000);
send2('loaded');
