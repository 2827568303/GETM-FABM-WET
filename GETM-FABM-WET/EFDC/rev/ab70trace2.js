'use strict';
function send2(s){ send(s); }
var T0=Date.now(); function t(){ return ((Date.now()-T0)/1000).toFixed(2); }
setTimeout(function(){
  [[0x156AB70,'ab70'],[0x156ACC0,'acc0'],[0x156B030,'b030']].forEach(function(pair){
    try{ Interceptor.attach(ptr(pair[0]),{ onEnter:function(){ send2('['+t()+'] ENTER '+pair[1]); }, onLeave:function(){ send2('['+t()+'] LEAVE '+pair[1]); } }); }catch(e){}
  });
  send2('hooked');
}, 200);
send2('loaded');
