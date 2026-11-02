'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
['0x156AB70','0x156ABA8','0x156ABD1','0x156ABD3','0x156ABDC','0x156AC31','0x156AC3F'].forEach(function(a){
  try{ Interceptor.attach(ptr(parseInt(a,16)), { onEnter:function(){ emit('HIT '+a); } }); }catch(e){ emit('fail '+a); }
});
emit('ready');
