'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
['0x156ABA8','0x156ABD1','0x156ABD3','0x156AC31','0x156AC3F','0x81D0D3','0x81D0DD'].forEach(function(a){
  try{ Interceptor.attach(ptr(parseInt(a,16)), { onEnter:function(){ emit('HIT '+a); } }); }catch(e){ emit('fail '+a); }
});
emit('ready');
