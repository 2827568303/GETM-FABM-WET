'use strict';
function send2(s){ send(s); }
var T0=Date.now(); function t(){ return ((Date.now()-T0)/1000).toFixed(2); }
setTimeout(function(){
  try{
    var obj=ptr(0x16249b0).readPointer();
    send2('['+t()+'] obj='+obj);
    if(obj.isNull()){ send2('null'); return; }
    var vt=obj.readPointer();
    var fn=vt.add(0x94).readPointer();
    send2('slot0x94='+fn);
    var f=new NativeFunction(fn,'uint',['pointer','int']);
    var hr=f(obj,-1);
    send2('['+t()+'] called Visible(True) hr=0x'+(hr>>>0).toString(16));
  }catch(e){ send2('ERR '+e); }
}, 8500);
send2('loaded');
