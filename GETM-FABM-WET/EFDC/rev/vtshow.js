'use strict';
function send2(s){ send(s); }
var T0=Date.now(); function t(){ return ((Date.now()-T0)/1000).toFixed(2); }
setTimeout(function(){
  try{
    var obj=ptr(0x16249b0).readPointer();
    send2('titleform obj='+obj);
    if(obj.isNull()) return;
    var vt=obj.readPointer();
    var m=vt.add(0x5c).readPointer();
    send2('vtable[0x5c]='+m);
    Interceptor.attach(m,{
      onEnter:function(a){ send2('['+t()+'] call vtable[0x5c] this='+a[0]+' arg='+a[1]); },
      onLeave:function(r){ send2('['+t()+'] -> hr=0x'+((r.toInt32()>>>0).toString(16))); }
    });
    send2('hooked');
  }catch(e){ send2('ERR '+e); }
}, 9000);
send2('loaded');
