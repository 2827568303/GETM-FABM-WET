'use strict';
function send2(s){ send(s); }
var T0=Date.now(); function t(){ return ((Date.now()-T0)/1000).toFixed(2); }
setTimeout(function(){
  [0x156AB70,0x156AC3F,0x81CDBF,0x81CDF7].forEach(function(va){
    try{ Interceptor.attach(ptr(va),{ onEnter:function(){ send2('['+t()+'] ENTER '+va.toString(16)); }, onLeave:function(){ send2('['+t()+'] LEAVE '+va.toString(16)); } }); }
    catch(e){ send2('fail '+va.toString(16)); }
  });
  send2('hooked');
}, 200);
send2('loaded');
