'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function hx(v){ return ('00000000'+(v>>>0).toString(16)).slice(-8); }
['0x156ABD1','0x156ABE1','0x156AC3F','0x156ABC6'].forEach(function(a){
  try{ Interceptor.attach(ptr(parseInt(a,16)), { onEnter: function(){ emit('HIT '+a); } }); }catch(e){ emit('hook fail '+a); }
});
var vb=Process.findModuleByName('MSVBVM60.DLL');
try{
  var p=vb.findExportByName('__vbaNew2');
  Interceptor.attach(p,{onEnter:function(a){ emit('__vbaNew2 classinfo='+a[0]); }});
}catch(e){}
emit('ready');
