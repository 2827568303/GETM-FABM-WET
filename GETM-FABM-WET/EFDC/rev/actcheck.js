'use strict';
function send2(s){ send(s); }
var T0=Date.now(); function t(){ return ((Date.now()-T0)/1000).toFixed(2); }
setTimeout(function(){
  try{
    var v=ptr(0x16203f4).readU16();
    send2('['+t()+'] [0x16203F4] = 0x'+v.toString(16));
    var w=ptr(0x16203f6).readU16();
    send2('['+t()+'] [0x16203F6] = 0x'+w.toString(16));
  }catch(e){ send2('ERR '+e); }
}, 3200);
setTimeout(function(){
  [0x81CDD5,0x81C922,0x156AB70,0x81CDF7].forEach(function(va){
    try{ Interceptor.attach(ptr(va),{ onEnter:function(){ send2('['+t()+'] HIT '+va.toString(16)); } }); }catch(e){}
  });
  send2('hooked');
}, 200);
send2('loaded');
