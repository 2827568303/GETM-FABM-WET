'use strict';
function send2(s){ send(s); }
var T0=Date.now(); function t(){ return ((Date.now()-T0)/1000).toFixed(2); }
var counts={};
setTimeout(function(){
  var u=Process.findModuleByName('user32.dll');
  ['PeekMessageA','GetMessageA','DispatchMessageA','PeekMessageW','GetMessageW'].forEach(function(fn){
    var p=u.findExportByName(fn); if(!p) return;
    try{ Interceptor.attach(p,{ onEnter:function(){ counts[fn]=(counts[fn]||0)+1; } }); }catch(e){}
  });
  send2('hooked msgloop');
}, 150);
setInterval(function(){ send2('['+t()+'] counts '+JSON.stringify(counts)); }, 3000);
send2('loaded');
