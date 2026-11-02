'use strict';
// diag72.js — 直接创建 frmEFDC_Explorer(0x482C3C)，并观察窗口
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }

var vb = Process.findModuleByName('MSVBVM60.DLL');
var New2 = new NativeFunction(vb.findExportByName('__vbaNew2'), 'void', ['pointer', 'pointer', 'pointer']);

var u32 = Process.findModuleByName('user32.dll');
var EnumWindows = new NativeFunction(u32.findExportByName('EnumWindows'), 'int', ['pointer', 'pointer']);
var GetClassNameW = new NativeFunction(u32.findExportByName('GetClassNameW'), 'int', ['pointer', 'pointer', 'int']);
var GetWindowTextW = new NativeFunction(u32.findExportByName('GetWindowTextW'), 'int', ['pointer', 'pointer', 'int']);
var IsWindowVisible = new NativeFunction(u32.findExportByName('IsWindowVisible'), 'int', ['pointer']);
var GetWindowThreadProcessId = new NativeFunction(u32.findExportByName('GetWindowThreadProcessId'), 'uint', ['pointer', 'pointer']);

var myPid = Process.id;

function list(tag){
  var out = [];
  var cb = new NativeCallback(function(h, l){
    var pidBuf = Memory.alloc(4);
    GetWindowThreadProcessId(h, pidBuf);
    if (pidBuf.readU32() !== myPid) return 1;
    var b = Memory.alloc(256);
    var n = GetClassNameW(h, b, 200);
    var cls = n > 0 ? b.readUtf16String(n) : '';
    if (cls.indexOf('Thunder') !== 0) return 1;
    var tb = Memory.alloc(256);
    var tn = GetWindowTextW(h, tb, 200);
    var title = tn > 0 ? tb.readUtf16String(tn) : '';
    out.push(cls + '|' + JSON.stringify(title) + '|vis=' + IsWindowVisible(h));
    return 1;
  }, 'int', ['pointer', 'pointer']);
  EnumWindows(cb, ptr(0));
  emit('  [' + tag + '] ' + (out.length ? out.join(' ;; ') : '<none>'));
}

var did = false;
Interceptor.attach(ptr(0x156AB70), { onEnter: function(){
  if (did) return;
  did = true;
  emit('helper hit; creating 0x482C3C');
  var out = Memory.alloc(4); out.writePointer(ptr(0));
  try {
    New2(ptr(0x482C3C), out, ptr(0));
    var obj = out.readPointer();
    emit('obj=' + obj + ' vtable=' + (obj.isNull() ? '<null>' : obj.readPointer()));
  } catch (e) { emit('New2 threw: ' + e); }
  list('after create (sync)');
}});
emit('diag72 ready');

