'use strict';
// diag64.js — 在 VB 窗体窗口创建瞬间（CreateWindowExA + atom）强制显示
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }

var u32 = Process.findModuleByName('user32.dll');
var GetClassNameW = new NativeFunction(u32.findExportByName('GetClassNameW'), 'int', ['pointer', 'pointer', 'int']);
var ShowWindow = new NativeFunction(u32.findExportByName('ShowWindow'), 'int', ['pointer', 'int']);
var IsWindowVisible = new NativeFunction(u32.findExportByName('IsWindowVisible'), 'int', ['pointer']);
var SetWindowLongW = new NativeFunction(u32.findExportByName('SetWindowLongW'), 'int', ['pointer', 'int', 'int']);
var UpdateWindow = new NativeFunction(u32.findExportByName('UpdateWindow'), 'int', ['pointer']);

Interceptor.attach(u32.findExportByName('CreateWindowExA'), {
  onLeave: function(r){
    if (r.isNull()) return;
    var cls = '';
    try { var b = Memory.alloc(256); var k = GetClassNameW(r, b, 200); cls = k > 0 ? b.readUtf16String(k) : ''; } catch (e) {}
    if (cls !== 'ThunderRT6FormDC') return;
    emit('form window created hwnd=' + r);
    try {
      var st = SetWindowLongW(r, -16, 0);
      SetWindowLongW(r, -16, (st | 0x10000000) & 0xFFFFFFFF);
      var prev = ShowWindow(r, 5);
      UpdateWindow(r);
      emit('  ShowWindow prev=' + prev + ' vis=' + IsWindowVisible(r));
    } catch (e) { emit('  show err ' + e); }
    setTimeout(function(){ emit('  later vis=' + IsWindowVisible(r) + ' title_check'); }, 1500);
  }
});
emit('diag64 ready');
