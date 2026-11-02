'use strict';
// diag109.js — 在 Sub Main 返回前，直接创建并 Show 主窗体 frmEFDC_Explorer(0x482C3C)
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }

var vb = Process.findModuleByName('MSVBVM60.DLL');
var New2 = new NativeFunction(vb.findExportByName('__vbaNew2'), 'void', ['pointer', 'pointer', 'pointer']);

var done = false;
Interceptor.attach(ptr(0x156831C), { onEnter: function(){
  if (done) return;
  done = true;
  emit('Sub Main about to return -> creating main form');
  var out = Memory.alloc(4); out.writePointer(ptr(0));
  try {
    New2(ptr(0x482C3C), out, ptr(0));
    var obj = out.readPointer();
    emit('main form obj=' + obj + ' vtable=' + (obj.isNull() ? '<null>' : obj.readPointer()));
    if (obj.isNull()) return;
    var vt = obj.readPointer();
    var slot = vt.add(0x2B0).readPointer();
    emit('show slot=' + slot);
    var showFn = new NativeFunction(slot, 'void', ['pointer', 'int', 'int', 'int', 'int']);
    showFn(obj, 2, 0, 1, 0);
    emit('Show called on main form');
  } catch (e) { emit('err ' + e); }
}});
emit('diag109 ready');

