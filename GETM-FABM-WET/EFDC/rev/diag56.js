'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function hx(v){ return ('00000000'+(v>>>0).toString(16)).slice(-8); }
Interceptor.attach(ptr(0x156ABAE), { onEnter: function(){
  try{
    var w = this.context.esp.add(0x10).readU16();
    var obj = ptr(0x16249B0).readPointer();
    emit('getter done: var.vt(word)=0x' + w.toString(16) + '  obj=' + obj + '  global2=' + hx(ptr(0x16204B4).readU32()));
  }catch(e){ emit('err '+e); }
}});
Interceptor.attach(ptr(0x156AC3F), { onEnter: function(){ emit('took SKIP branch (0x156AC3F)'); } });
Interceptor.attach(ptr(0x156ABE1), { onEnter: function(){ emit('took CREATE branch (0x48FE70)'); } });
emit('ready');
