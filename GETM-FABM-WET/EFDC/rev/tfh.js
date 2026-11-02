'use strict';
function send2(s){ send(s); }
var T0=Date.now(); function t(){ return ((Date.now()-T0)/1000).toFixed(2); }
setTimeout(function(){
  [0x156AB70,0x156AEC0,0x156AF20,0x156B030,0x156B0E0,0x156ACC0].forEach(function(va){
    try{ Interceptor.attach(ptr(va),{ onEnter:function(){ send2('['+t()+'] ENTER '+va.toString(16)); }, onLeave:function(){ send2('['+t()+'] LEAVE '+va.toString(16)); } }); send2('hooked '+va.toString(16)); }
    catch(e){ send2('fail '+va.toString(16)+' '+e); }
  });
}, 200);
send2('loaded');
