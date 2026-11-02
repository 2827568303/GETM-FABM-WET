'use strict';
// diag79.js — 用 int3 断点确认 0x156ABAE / 0x156ABD1 / 0x156AC31 是否真的被执行
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }

var targets = [0x156ABAE, 0x156ABD1, 0x156AC31];
var targetSet = {};
targets.forEach(function(a){ targetSet[a] = true; });

Process.setExceptionHandler(function(details){
  try {
    var pc = details.context.pc;
    var addr = parseInt(pc.toString(), 16);
    if (targetSet[addr]) {
      emit('INT3 HIT at 0x' + addr.toString(16));
      details.context.pc = pc.add(1);
      return true;
    }
    emit('exception at ' + pc + ' type=' + details.type);
    return false;
  } catch (e) {
    emit('handler err ' + e);
    return false;
  }
});

targets.forEach(function(a){
  try {
    var p = ptr(a);
    Memory.protect(p, 1, 'rwx');
    p.writeU8(0xCC);
    emit('breakpoint set at 0x' + a.toString(16));
  } catch (e) { emit('set fail 0x' + a.toString(16) + ': ' + e); }
});
emit('diag79 ready');
