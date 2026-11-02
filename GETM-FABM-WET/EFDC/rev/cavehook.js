'use strict';
function send2(s){ send(s); }
setTimeout(function(){
  var m=Process.findModuleByName('MSVBVM60.dll')||Process.findModuleByName('MSVBVM60.DLL');
  send2('base='+m.base+' name='+m.name);
  var cave=m.base.add(0x105600);
  try{
    Interceptor.attach(cave,{
      onEnter:function(){ send2('ENTER cave'); this.ebp=this.context.ebp; },
      onLeave:function(r){ send2('LEAVE cave -> eax=0x'+(r.toInt32()>>>0).toString(16)); }
    });
    send2('hooked cave at '+cave);
  }catch(e){ send2('hook err '+e); }
}, 500);
send2('loaded');
