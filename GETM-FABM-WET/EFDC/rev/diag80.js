'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
var targets=[0x156ABAE,0x156ABD1,0x156AC31];
var set={};
targets.forEach(function(a){ set[a]=true; });
Process.setExceptionHandler(function(d){
  try{
    if(d.type!=='breakpoint') return false;
    var pc=d.context.pc; var addr=parseInt(pc.toString(),16);
    emit('INT3 at 0x'+addr.toString(16)+' (wanted='+(set[addr]?'yes':'no')+')');
    d.context.pc=pc.add(1);
    return true;
  }catch(e){ return false; }
});
targets.forEach(function(a){
  try{ var p=ptr(a); Memory.protect(p,1,'rwx'); p.writeU8(0xCC); emit('bp 0x'+a.toString(16)); }catch(e){ emit('fail 0x'+a.toString(16)); }
});
emit('ready');
