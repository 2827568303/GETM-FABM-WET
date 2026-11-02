'use strict';
// diag14.js — 在 CheckLicensing 返回处强行创建主窗体并显示
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }
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
var injected = false;

function listWindows(tag){
  var out = [];
  var cb = new NativeCallback(function(h, l){
    var buf = Memory.alloc(512);
    var n = GetClassNameW(h, buf, 240);
    var cls = n > 0 ? buf.readUtf16String(n) : '';
    if (cls.indexOf('Thunder') === 0) {
      var tb = Memory.alloc(512);
      var tn = GetWindowTextW(h, tb, 240);
      var title = tn > 0 ? tb.readUtf16String(tn) : '';
      out.push(cls + ' | ' + JSON.stringify(title) + ' | vis=' + IsWindowVisible(h) + ' | ' + h);
      if (tag === 'show') {
        var r = ShowWindow(h, 5);
        emit('    ShowWindow(' + h + ',SW_SHOW) -> ' + r + ' now vis=' + IsWindowVisible(h));
      }
    }
    return 1;
  }, 'int', ['pointer', 'pointer']);
  EnumWindows(cb, ptr(0));
  emit('  窗口[' + tag + ']: ' + (out.length ? out.join(' ;; ') : '<none>'));
}

Interceptor.attach(ptr(0x81C4C0), {
  onEnter: function(){ emit('ENTER CheckLicensing'); },
  onLeave: function(r){
    emit('LEAVE CheckLicensing ret=' + r.toInt32());
    if (injected) return;
    injected = true;
    var cur = GLOB.readPointer();
    emit('  全局窗体对象=' + cur);
    var cands = [0x482C3C, 0x4D5204];
    for (var i = 0; i < cands.length; i++) {
      var out = Memory.alloc(4); out.writePointer(ptr(0));
      try {
        New2(ptr(cands[i]), out, ptr(0));
        var obj = out.readPointer();
        emit('  New2(' + hx(cands[i]) + ') -> ' + obj);
        if (!obj.isNull()) {
          GLOB.writePointer(obj);
          emit('  写入全局 ' + obj + ' vtable=' + obj.readPointer());
        }
      } catch (e) { emit('  New2 异常: ' + e); }
      listWindows('after ' + hx(cands[i]));
    }
    setTimeout(function(){ listWindows('show'); }, 150);
    setTimeout(function(){ listWindows('show2'); }, 1200);
    setTimeout(function(){ listWindows('show3'); }, 4000);
  }
});
emit('diag14 ready');
