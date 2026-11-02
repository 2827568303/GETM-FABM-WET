'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function hookf(a,name){
  try{
    Interceptor.attach(ptr(parseInt(a,16)),{
      onLeave:function(r){ emit(name+' -> 0x'+(r.toInt32()>>>0).toString(16)+' (ax=0x'+(r.toInt32()&0xffff).toString(16)+')'); }
    });
    emit('hooked '+name);
  }catch(e){ emit('fail '+name); }
}
hookf('0x82E280','checkA');
hookf('0x82E240','checkB');
hookf('0x82E2C0','checkC');
try{ Interceptor.attach(ptr(0x81CA01),{onEnter:function(){ emit('at 0x81CA01 jne: eax=0x'+(this.context.eax.toInt32()>>>0).toString(16)+' ebx=0x'+(this.context.ebx.toInt32()>>>0).toString(16)); }}); }catch(e){}
emit('ready');
