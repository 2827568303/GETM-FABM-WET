'use strict';
// diag40.js — 窗体创建后立刻调用方法 ID 0x94（疑似 Show），看能否真正显示
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function hx(v){ return ('00000000'+(v>>>0).toString(16)).slice(-8); }

var GLOB = ptr(0x16249B0);
var done = false;

Interceptor.attach(ptr(0x156ABA0), { onEnter: function(){
  if (done) return;
  done = true;
  var obj = GLOB.readPointer();
  emit('form object = ' + obj);
  if (obj.isNull()) return;
  var vt = obj.readPointer();
  emit('vtable = ' + vt);
  var fn = new NativeFunction(vt.add(0x250).readPointer(), 'void', ['pointer', 'pointer']);
  var v = Memory.alloc(32);
  v.writeU32(0);
  emit('calling method[0x250](obj, &var) ...');
  try { fn(obj, v); emit('  returned; var.vt=' + v.readU16()); }
  catch (e) { emit('  call threw: ' + e); }
  var u32 = Process.findModuleByName('user32.dll');
  var EnumWindows = new NativeFunction(u32.findExportByName('EnumWindows'), 'int', ['pointer', 'pointer']);
  var GetClassNameW = new NativeFunction(u32.findExportByName('GetClassNameW'), 'int', ['pointer', 'pointer', 'int']);
  var IsWindowVisible = new NativeFunction(u32.findExportByName('IsWindowVisible'), 'int', ['pointer']);
  var found = [];
  var cb = new NativeCallback(function(h, l){
    var b = Memory.alloc(512);
    var n = GetClassNameW(h, b, 200);
    var cls = n > 0 ? b.readUtf16String(n) : '';
    if (cls.indexOf('ThunderRT6Form') === 0) found.push(cls + '|vis=' + IsWindowVisible(h) + '|' + h);
    return 1;
  }, 'int', ['pointer', 'pointer']);
  EnumWindows(cb, ptr(0));
  emit('windows after call: ' + (found.length ? found.join(' ;; ') : '<none>'));
}});
emit('diag40 ready');
