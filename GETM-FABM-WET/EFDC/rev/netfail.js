'use strict';
function send2(s){ send(s); }
var T0=Date.now(); function t(){ return ((Date.now()-T0)/1000).toFixed(2); }
var n=0, done=false;
var iv=setInterval(function(){
  if(done) return;
  var m=Process.findModuleByName('winhttp.dll'); if(!m) return;
  var p=m.findExportByName('WinHttpConnect'); if(!p) return;
  done=true; clearInterval(iv);
  Interceptor.attach(p,{
    onEnter:function(a){ n++; this.i=n; send2('['+t()+'] WinHttpConnect #'+n); },
    onLeave:function(r){
      if(this.i>=2){ send2('['+t()+'] -> forcing FAILURE on #'+this.i); r.replace(ptr(0)); }
    }
  });
  send2('hooked');
}, 200);
setTimeout(function(){ clearInterval(iv); }, 12000);
send2('loaded');
