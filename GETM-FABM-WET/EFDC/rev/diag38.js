'use strict';
// diag38.js — 在窗体创建的瞬间立刻 ShowWindow（同线程）
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }

var u32 = Process.findModuleByName('user32.dll');
var ShowWindow = new NativeFunction(u32.findExportByName('ShowWindow'), 'int', ['pointer', 'int']);
var IsWindowVisible = new NativeFunction(u32.findExportByName('IsWindowVisible'), 'int', ['pointer']);
var SetWindowLongW = new NativeFunction(u32.findExportByName('SetWindowLongW'), 'int', ['pointer', 'int', 'int']);

Interceptor.attach(u32.findExportByName('CreateWindowExW'), {
  onEnter: function(a){
    try{
      var cls = a[1].readUtf16String();
      this.target = /ThunderRT6Form/.test(cls) ? cls : null;
      this.title = a[2].isNull() ? '' : a[2].readUtf16String();
    }catch(e){ this.target = null; }
  },
  onLeave: function(r){
    if (!this.target) return;
    try{
      emit('Created ' + this.target + ' title=' + JSON.stringify(this.title) + ' hwnd=' + r);
      var style = SetWindowLongW(r, -16, 0);
      var s = SetWindowLongW(r, -16, (style | 0x10000000) | 0);   // WS_VISIBLE
      var prev = ShowWindow(r, 5);
      emit('  ShowWindow -> prev=' + prev + ' vis=' + IsWindowVisible(r));
    }catch(e){ emit('  show err ' + e); }
  }
});
emit('diag38 ready');
