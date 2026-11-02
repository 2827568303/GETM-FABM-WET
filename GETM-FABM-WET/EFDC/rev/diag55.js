'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function hx(v){ return ('00000000'+(v>>>0).toString(16)).slice(-8); }
try{
  Interceptor.attach(ptr(0x81C4C0), { onEnter: function(){ emit('ENTER CheckLicensing  caller_ret=' + hx(this.returnAddress.toInt32())); } });
}catch(e){ emit('h1 '+e); }
try{
  Interceptor.attach(ptr(0x81D0D3), { onEnter: function(){ emit('HIT epilogue 0x81D0D3'); } });
}catch(e){ emit('h2 '+e); }
try{
  Interceptor.attach(ptr(0x81D0DD), { onEnter: function(){ emit('HIT 0x81D0DD'); } });
}catch(e){ emit('h3 '+e); }
emit('ready');
