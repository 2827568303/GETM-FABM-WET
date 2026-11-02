'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function tryHook(){
  var m=Process.findModuleByName('winhttp.dll');
  if(!m){ emit('winhttp not loaded yet'); return; }
  ['WinHttpConnect','WinHttpOpenRequest','WinHttpSendRequest','WinHttpReceiveResponse','WinHttpOpen'].forEach(function(n){
    var p=m.findExportByName(n);
    if(!p) return;
    Interceptor.attach(p,{onEnter:function(a){
      var s=n;
      try{
        if(n==='WinHttpConnect') s+=' host='+a[1].readUtf16String()+' port='+a[2].toInt32();
        if(n==='WinHttpOpenRequest') s+=' verb='+a[1].readUtf16String()+' path='+a[2].readUtf16String();
        if(n==='WinHttpOpen') s+=' agent='+(a[0].isNull()?'':a[0].readUtf16String());
      }catch(e){}
      emit(s);
    }});
  });
  emit('winhttp hooks installed');
}
setTimeout(tryHook, 1500);
emit('ready');
