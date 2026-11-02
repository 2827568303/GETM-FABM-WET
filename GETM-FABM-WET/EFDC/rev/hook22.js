'use strict';
function send2(s){ send(s); }
var T0=Date.now(); function t(){ return ((Date.now()-T0)/1000).toFixed(2); }
setTimeout(function(){
  try{
    var m=Process.findModuleByName('oleaut32.dll');
    var b=m.base;
    function hookOff(rva,name){
      try{ Interceptor.attach(b.add(rva), {
        onEnter:function(a){ send2('['+t()+'] ENTER '+name+' a0='+a[0]+' a1='+a[1]+' a2='+a[2]); },
        onLeave:function(r){ send2('['+t()+'] LEAVE '+name+' ret='+r+' eax='+(this.context.eax.toInt32()>>>0).toString(16)); }
      }); send2('hooked '+name+' @'+b.add(rva)); }catch(e){ send2('hook fail '+name+' '+e); }
    }
    hookOff(0x3dcee,'init_flag');
    hookOff(0x3e39c,'init_worker');
    send2('base='+b);
  }catch(e){ send2('err '+e); }
}, 300);
send2('loaded');
