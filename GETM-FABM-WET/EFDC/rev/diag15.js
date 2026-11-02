'use strict';
// diag15.js — 用替身替换 Sub Main：直接创建主窗体并显示，然后返回让 VB6 运行时进入消息循环
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function hx(v){ return ('00000000'+(v>>>0).toString(16)).slice(-8); }

var vb = Process.findModuleByName('MSVBVM60.DLL');
var New2 = new NativeFunction(vb.findExportByName('__vbaNew2'), 'void', ['pointer', 'pointer', 'pointer']);
var u32 = Process.findModuleByName('user32.dll');
var EnumWindows = new NativeFunction(u32.findExportByName('EnumWindows'), 'int', ['pointer', 'pointer']);
var GetClassNameW = new NativeFunction(u32.findExportByName('GetClassNameW'), 'int', ['pointer', 'pointer', 'int']);
var GetWindowTextW = new NativeFunction(u32.findExportByName('GetWindowTextW'), 'int', ['pointer', 'pointer', 'int']);
var ShowWindow = new NativeFunction(u32.findExportByName('ShowWindow'), 'int', ['pointer', 'int']);
var IsWindowVisible = new NativeFunction(u32.findExportByName('IsWindowVisible'), 'int', ['pointer']);

var GLOB = ptr(0x16249B0);

function listWindows(tag, show){
  var out = [];
  var cb = new NativeCallback(function(h, l){
    var buf = Memory.alloc(512);
    var n = GetClassNameW(h, buf, 200);
    var cls = n > 0 ? buf.readUtf16String(n) : '';
    if (cls.indexOf('Thunder') === 0) {
      var tb = Memory.alloc(512);
      var tn = GetWindowTextW(h, tb, 200);
      var title = tn > 0 ? tb.readUtf16String(tn) : '';
      out.push(cls + '|' + JSON.stringify(title) + '|vis=' + IsWindowVisible(h) + '|' + h);
      if (show) { ShowWindow(h, 5); out.push('  shown->' + IsWindowVisible(h)); }
    }
    return 1;
  }, 'int', ['pointer', 'pointer']);
  EnumWindows(cb, ptr(0));
  emit('  [' + tag + '] ' + (out.length ? out.join(' ;; ') : '<no thunder window>'));
}

var done = false;
var stub = new NativeCallback(function(){
  emit('SUBMAIN-STUB 进入');
  if (done) return;
  done = true;
  var cands = [0x482C3C, 0x4D5204];
  for (var i = 0; i < cands.length; i++) {
    var out = Memory.alloc(4); out.writePointer(ptr(0));
    try {
      New2(ptr(cands[i]), out, ptr(0));
      var obj = out.readPointer();
      emit('  New2(' + hx(cands[i]) + ') -> ' + obj);
      if (!obj.isNull()) {
        GLOB.writePointer(obj);
        emit('  vtable=' + obj.readPointer());
      }
    } catch (e) { emit('  New2 err ' + e); }
    listWindows('after New2 ' + hx(cands[i]), false);
  }
  listWindows('final', true);
  setTimeout(function(){ listWindows('later', true); }, 800);
  setTimeout(function(){ listWindows('later2', true); }, 3000);
}, 'void', []);

Interceptor.replace(ptr(0x1568180), stub);
emit('diag15 ready (Sub Main replaced)');
