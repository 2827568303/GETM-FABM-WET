'use strict';
// diag30.js — 在 SoftModalMessageBox 时刻扫描栈，找出 app 侧调用帧（用于定位错误处理代码）
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function hx(v){ return ('00000000'+(v>>>0).toString(16)).slice(-8); }

var u32 = Process.findModuleByName('user32.dll');
var pSoft = u32.findExportByName('SoftModalMessageBox');
var done = false;

Interceptor.attach(pSoft, { onEnter: function(a){
  if (done) return;
  done = true;
  var pms = a[0];
  var t = pms.add(0xC).readPointer();
  emit('MSG: ' + JSON.stringify(t.isNull()?'':t.readUtf16String()));
  var esp = this.context.esp;
  var hits = [];
  var seen = {};
  for (var off = 0; off < 0x4000; off += 4) {
    var v;
    try { v = esp.add(off).readU32() >>> 0; } catch (e) { break; }
    if (v >= 0x401000 && v < 0x161F000) {
      if (!seen[v]) { seen[v] = 1; hits.push([off, v]); }
    }
  }
  emit('stack 中的 exe 代码地址（' + hits.length + ' 个）:');
  for (var i = 0; i < hits.length && i < 20; i++) {
    emit('  [+0x' + hits[i][0].toString(16) + '] ' + hx(hits[i][1]) + '  (exe+' + hx(hits[i][1] - 0x400000) + ')');
  }
}});
emit('diag30 ready');
