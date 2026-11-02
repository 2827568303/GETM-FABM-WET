'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function h(a,name,fn){
  try{ Interceptor.attach(ptr(parseInt(a,16)), fn); emit('attached '+name); }
  catch(e){ emit('ATTACH FAIL '+name+' : '+e); }
}
h('0x156ABAE','after-getter',{onEnter:function(){
  var eax=this.context.eax.toInt32();
  var w=0; try{ w=this.context.esp.add(0x10).readU16(); }catch(e){}
  emit('after getter: eax=0x'+(eax>>>0).toString(16)+'  var.word=0x'+w.toString(16));
}});
h('0x156ABB2','jge',{onEnter:function(){ emit('at jge (eax=0x'+(this.context.eax.toInt32()>>>0).toString(16)+')'); }});
h('0x156ABC6','cmp',{onEnter:function(){ emit('at cmp'); }});
h('0x156ABD1','je',{onEnter:function(){ emit('at je'); }});
emit('ready');
