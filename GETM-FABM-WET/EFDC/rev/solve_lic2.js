'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
[[0xB9C237,'after_check'],[0xB9C258,'fpu_cmp'],[0xB9C25E,'ERROR_PATH'],[0xB9C3AC,'SAFE_PATH']].forEach(function(p){
  try{ Interceptor.attach(ptr(p[0]), { onEnter:function(){
    var ax=this.context.eax.toInt32() & 0xffff;
    emit(p[1]+'  eax=0x'+(this.context.eax.toInt32()>>>0).toString(16));
  }}); }catch(e){ emit('fail '+p[1]+' '+e); }
});
emit('ready');
