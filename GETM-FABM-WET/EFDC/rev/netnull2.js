'use strict';
function send2(s){ send(s); }
var done=false;
var iv=setInterval(function(){
  if(done) return;
  var m=Process.findModuleByName('winhttp.dll'); if(!m) return;
  var p=m.findExportByName('WinHttpConnect'); if(!p) return;
  done=true; clearInterval(iv);
  Interceptor.attach(p,{ onLeave:function(r){ r.replace(ptr(0)); } });
  send2('WinHttpConnect -> NULL');
}, 150);
setTimeout(function(){ clearInterval(iv); }, 12000);
send2('loaded');
