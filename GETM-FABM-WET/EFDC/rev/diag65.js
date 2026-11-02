'use strict';
// diag65.js — 窗体创建后立刻调用 vtable 槽 0x94（最可能的 Show）
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function hx(v){ return ('00000000'+(v>>>0).toString(16)).slice(-8); }

var vb = Process.findModuleByName('MSVBVM60.DLL');
var pNew2 = vb.findExportByName('__vbaNew2');
var done = {};

Interceptor.attach(pNew2, {
  onEnter: function(a){ this.out = a[1]; this.ci = a[0]; },
  onLeave: function(){
    var ok = false;
    try { ok = (this.ci.toInt32() >>> 0) === 0x4D5204; } catch (e) {}
    if (!ok) return;
    var obj = null;
    try { obj = this.out.readPointer(); } catch (e) {}
    if (!obj || obj.isNull()) return;
    var key = obj.toString();
    if (done[key]) return;
    done[key] = 1;
    emit('form obj=' + obj + ' vtable=' + obj.readPointer());
    var vt = obj.readPointer();
    var fn = new NativeFunction(vt.add(0x94).readPointer(), 'void', ['pointer', 'pointer']);
    var v = Memory.alloc(32);
    v.writeU32(0);
    emit('calling [obj+0x94](obj, &var)');
    try {
      fn(obj, v);
      emit('  ok; var.vt=' + v.readU16());
    } catch (e) { emit('  threw: ' + e); }
    var u32 = Process.findModuleByName('user32.dll');
    var EnumWindows = new NativeFunction(u32.findExportByName('EnumWindows'), 'int', ['pointer', 'pointer']);
    var GetClassNameW = new NativeFunction(u32.findExportByName('GetClassNameW'), 'int', ['pointer', 'pointer', 'int']);
    var IsWindowVisible = new NativeFunction(u32.findExportByName('IsWindowVisible'), 'int', ['pointer']);
    var found = [];
    var cb = new NativeCallback(function(h, l){
      var b = Memory.alloc(256);
      var n = GetClassNameW(h, b, 200);
      var cls = n > 0 ? b.readUtf16String(n) : '';
      if (cls.indexOf('ThunderRT6Form') === 0) found.push(cls + '|vis=' + IsWindowVisible(h));
      return 1;
    }, 'int', ['pointer', 'pointer']);
    EnumWindows(cb, ptr(0));
    emit('  windows: ' + found.join(' ;; '));
  }
});
emit('diag65 ready');
