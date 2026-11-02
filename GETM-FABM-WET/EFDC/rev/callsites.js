'use strict';
function send2(s){ send(s); }
var T0=Date.now(); function t(){ return ((Date.now()-T0)/1000).toFixed(2); }
setTimeout(function(){
  [0x156AD74,0x156ADB9,0x156AE23,0x156AF8E,0x156AFD2,0x156AFE6,0x156B099].forEach(function(va){
    try{ Interceptor.attach(ptr(va),{ onEnter:function(){ send2('['+t()+'] hit '+va.toString(16)); } }); }catch(e){ send2('fail '+va.toString(16)+' '+e); }
  });
  send2('hooked callsites');
}, 250);
send2('loaded');
