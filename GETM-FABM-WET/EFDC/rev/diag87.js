'use strict';
// diag87.js — 用 Frida 读取阻塞线程的上下文与栈，找出调用链
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }

var u32 = Process.findModuleByName('user32.dll');
var EnumWindows = new NativeFunction(u32.findExportByName('EnumWindows'), 'int', ['pointer', 'pointer']);
var GetClassNameW = new NativeFunction(u32.findExportByName('GetClassNameW'), 'int', ['pointer', 'pointer', 'int']);
var GetWindowThreadProcessId = new NativeFunction(u32.findExportByName('GetWindowThreadProcessId'), 'uint', ['pointer', 'pointer']);
var myPid = Process.id;

function formThread(){
  var tid = 0;
  var cb = new NativeCallback(function(h, l){
    var p = Memory.alloc(4); GetWindowThreadProcessId(h, p);
    if (p.readU32() !== myPid) return 1;
    var b = Memory.alloc(256); var n = GetClassNameW(h, b, 200);
    var cls = n > 0 ? b.readUtf16String(n) : '';
    if (cls.indexOf('ThunderRT6Form') === 0) {
      tid = p.readU32();
    }
    return 1;
  }, 'int', ['pointer', 'pointer']);
  EnumWindows(cb, ptr(0));
  return tid;
}

setTimeout(function(){
  var tid = formThread();
  emit('form thread=' + tid);
  var ths = Process.enumerateThreads();
  for (var i = 0; i < ths.length; i++) {
    var th = ths[i];
    if (th.id !== tid) continue;
    var c = th.context || {};
    emit('thread ' + th.id + ' pc=' + (c.pc ? mod(c.pc) : '?') + ' esp=' + (c.sp || '?'));
    var sp = c.sp;
    if (!sp) { emit('  no sp'); return; }
    var hits = [];
    for (var off = 0; off < 0x2000; off += 4) {
      var v;
      try { v = sp.add(off).readU32() >>> 0; } catch (e) { break; }
      if ((v >= 0x401000 && v < 0x161F000) || (v >= 0x60000000 && v < 0x64000000)) hits.push([off, v]);
    }
    emit('  stack code hits: ' + hits.length);
    for (var j = 0; j < Math.min(hits.length, 30); j++) {
      emit('   [sp+0x' + hits[j][0].toString(16) + '] 0x' + hits[j][1].toString(16) + '  ' + mod(ptr(hits[j][1])));
    }
  }
}, 9000);
emit('diag87 ready');
