'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
['0x81CDBF','0x81CA07','0x81D3E0','0x81CD9B','0x81C4C0','0x828F50','0x156ACC0','0x81D0F0'].forEach(function(a){
  try{ Interceptor.attach(ptr(parseInt(a,16)), { onEnter: function(){ emit('HIT '+a); }, onLeave: function(){ emit('  leave '+a); } }); }catch(e){ emit('hook fail '+a); }
});
emit('ready');
