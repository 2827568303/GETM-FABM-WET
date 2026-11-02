'use strict';
// diag66.js — 在窗体创建后调用指定 vtable 槽，观察是否真正显示（SLOT 由外部注入）
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }

var u32 = Process.findModuleByName('user32.dll');
var EnumWindows = new NativeFunction(u32.findExportByName('EnumWindows'), 'int', ['pointer', 'pointer']);
var GetClassNameW = new NativeFunction(u32.findExportByName('GetClassNameW'), 'int', ['pointer', 'pointer', 'int']);
var IsWindowVisible = new NativeFunction(u32.findExportByName('IsWindowVisible'), 'int', ['pointer']);

function list(tag){
  var out = [];
  var cb = new NativeCallback(function(h, l){
    var b = Memory.alloc(256);
    var n = GetClassNameW(h, b, 200);
    var cls = n > 0 ? b.readUtf16String(n) : '';
    if (cls.indexOf('ThunderRT6Form') === 0) out.push(h + '|vis=' + IsWindowVisible(h));
    return 1;
  }, 'int', ['pointer', 'pointer']);
  EnumWindows(cb, ptr(0));
  emit('  [' + tag + '] ' + (out.length ? out.join(' ;; ') : '<none>'));
}

var vb = Process.findModuleByName('MSVBVM60.DLL');
var done = {};
Interceptor.attach(vb.findExportByName('__vbaNew2'), {
  onEnter: function(a){ this.out = a[1]; this.ci = a[0]; },
  onLeave: function(){
    var isForm = false;
    try { isForm = (this.ci.toInt32() >>> 0) === 0x4D5204; } catch (e) {}
    if (!isForm) return;
    var obj = null;
    try { obj = this.out.readPointer(); } catch (e) { return; }
    if (!obj || obj.isNull()) return;
    var k = obj.toString();
    if (done[k]) return;
    done[k] = 1;
    emit('form obj=' + obj + ' vtable=' + obj.readPointer() + '  calling slot 0x' + SLOT.toString(16));
    try {
      var vt = obj.readPointer();
      var fn = new NativeFunction(vt.add(SLOT).readPointer(), 'void', ['pointer']);
      fn(obj);
      emit('  slot call returned (1 arg)');
    } catch (e) { emit('  slot call threw: ' + e); }
    setTimeout(function(){ list('t+400ms'); }, 400);
    setTimeout(function(){ list('t+1600ms'); }, 1600);
    setTimeout(function(){ list('t+3600ms'); }, 3600);
  }
});
emit('diag66 ready');

