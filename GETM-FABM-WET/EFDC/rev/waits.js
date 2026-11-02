'use strict';
function send2(s){ send(s); }
function sym(a){ try{ var m=Process.findModuleByAddress(a); if(m) return m.name+'+0x'+a.sub(m.base).toString(16);}catch(e){} return null; }
setTimeout(function(){
  var k=Process.findModuleByName('kernel32.dll');
  ['WaitForSingleObject','WaitForSingleObjectEx','WaitForMultipleObjects','MsgWaitForMultipleObjects','MsgWaitForMultipleObjectsEx'].forEach(function(fn){
    var p=k.findExportByName(fn); if(!p) return;
    try{
      Interceptor.attach(p,{
        onEnter:function(a){
          var t=a[1].toInt32();
          if(t!==-1 && t<3000) return;
          if(this.reported) return; this.reported=1;
          var bt=Thread.backtrace(this.context,Backtracer.FUZZY).map(sym).filter(Boolean).slice(0,8).join(' <- ');
          send2(fn+' handle='+a[0]+' timeout='+t+' | '+bt);
        }
      });
    }catch(e){}
  });
  send2('hooks ready');
}, 150);
send2('loaded');
