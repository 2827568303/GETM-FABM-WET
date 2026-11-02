'use strict';
function send2(s){ send(s); }
var T0=Date.now();
function t(){ return ((Date.now()-T0)/1000).toFixed(2); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); if(m) return m.name+'+0x'+a.sub(m.base).toString(16);}catch(e){} return String(a); }
function hook(modName, fn, onEnter, onLeave){
  var m=Process.findModuleByName(modName); if(!m){ send2('!! missing '+modName); return; }
  var a=m.findExportByName(fn); if(!a){ send2('!! missing '+fn); return; }
  Interceptor.attach(a,{onEnter:onEnter,onLeave:onLeave}); send2('hooked '+fn);
}
hook('msvbvm60.dll','__vbaNew2',function(args){
  send2('['+t()+'] __vbaNew2 info='+args[0]+' out='+args[1]+' from='+mod(this.returnAddress));
},function(ret){ send2('['+t()+']   -> hr=0x'+(ret.toInt32()>>>0).toString(16)); });
hook('msvbvm60.dll','__vbaNew',function(args){
  send2('['+t()+'] __vbaNew info='+args[0]+' from='+mod(this.returnAddress));
},function(ret){ send2('['+t()+']   -> hr=0x'+(ret.toInt32()>>>0).toString(16)); });
send2('loaded');
