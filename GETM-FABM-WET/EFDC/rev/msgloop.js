'use strict';
function send2(s){ send(s); }
var T0=Date.now(); function t(){ return ((Date.now()-T0)/1000).toFixed(2); }
var cnt={};
setTimeout(function(){
  var u=Process.findModuleByName('user32.dll');
  ['GetMessageA','GetMessageW','PeekMessageA','PeekMessageW','DispatchMessageA','DispatchMessageW'].forEach(function(fn){
    var p=u.findExportByName(fn); if(!p) return;
    try{ Interceptor.attach(p,{ onEnter:function(){ cnt[fn]=(cnt[fn]||0)+1; } }); send2('hooked '+fn); }catch(e){}
  });
  setTimeout(function(){ send2('counts: '+JSON.stringify(cnt)); }, 9000);
}, 250);
send2('loaded');
