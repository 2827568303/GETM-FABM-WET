'use strict';
// diag16.js — 暴力枚举所有 class info：逐个 New2，记录产生的窗口类别（找 MDI 主窗体）
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(7,' ')+' '+s); }
function hx(v){ return ('00000000'+(v>>>0).toString(16)).slice(-8); }

var vb = Process.findModuleByName('MSVBVM60.DLL');
var New2 = new NativeFunction(vb.findExportByName('__vbaNew2'), 'void', ['pointer', 'pointer', 'pointer']);
var u32 = Process.findModuleByName('user32.dll');
var EnumWindows = new NativeFunction(u32.findExportByName('EnumWindows'), 'int', ['pointer', 'pointer']);
var GetClassNameW = new NativeFunction(u32.findExportByName('GetClassNameW'), 'int', ['pointer', 'pointer', 'int']);
var GetWindowTextW = new NativeFunction(u32.findExportByName('GetWindowTextW'), 'int', ['pointer', 'pointer', 'int']);
var GetWindowLongW = new NativeFunction(u32.findExportByName('GetWindowLongW'), 'int', ['pointer', 'int']);

function scan(tag){
  var hits = [];
  var cb = new NativeCallback(function(h, l){
    var buf = Memory.alloc(512);
    var n = GetClassNameW(h, buf, 200);
    var cls = n > 0 ? buf.readUtf16String(n) : '';
    if (cls.indexOf('Thunder') === 0 && cls !== 'ThunderRT6Main') {
      var tb = Memory.alloc(512);
      var tn = GetWindowTextW(h, tb, 200);
      hits.push(cls + '|' + JSON.stringify(tn > 0 ? tb.readUtf16String(tn) : '') + '|' + h);
    }
    return 1;
  }, 'int', ['pointer', 'pointer']);
  EnumWindows(cb, ptr(0));
  return hits;
}

var done = false;
var stub = new NativeCallback(function(){
  if (done) return;
  done = true;
  emit('STUB 开始枚举 ' + CIS.length + ' 个 class info');
  var out = Memory.alloc(4);
  for (var i = 0; i < CIS.length; i++) {
    out.writePointer(ptr(0));
    var ok = true;
    try { New2(ptr(CIS[i]), out, ptr(0)); } catch (e) { ok = false; emit('  ci=' + hx(CIS[i]) + ' New2 异常'); }
    if (!ok) continue;
    var w = scan('x');
    if (w.length) emit('ci=' + hx(CIS[i]) + ' -> ' + w.join(' ;; '));
    else if (i % 20 === 0) emit('  ..ci=' + hx(CIS[i]) + ' (无窗口)');
  }
  emit('枚举结束');
}, 'void', []);

Interceptor.replace(ptr(0x1568180), stub);
emit('diag16 ready');
