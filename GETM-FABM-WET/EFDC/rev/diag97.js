'use strict';
// diag97.js — 在主线程的长等待期间（WaitForMultipleObjects）顺便把窗体显示出来
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }

var k32 = Process.findModuleByName('kernel32.dll');
var u32 = Process.findModuleByName('user32.dll');
var EnumWindows = new NativeFunction(u32.findExportByName('EnumWindows'), 'int', ['pointer', 'pointer']);
var GetClassNameW = new NativeFunction(u32.findExportByName('GetClassNameW'), 'int', ['pointer', 'pointer', 'int']);
var GetWindowTextW = new NativeFunction(u32.findExportByName('GetWindowTextW'), 'int', ['pointer', 'pointer', 'int']);
var IsWindowVisible = new NativeFunction(u32.findExportByName('IsWindowVisible'), 'int', ['pointer']);
var ShowWindow = new NativeFunction(u32.findExportByName('ShowWindow'), 'int', ['pointer', 'int']);
var SetWindowLongW = new NativeFunction(u32.findExportByName('SetWindowLongW'), 'int', ['pointer', 'int', 'int']);
var UpdateWindow = new NativeFunction(u32.findExportByName('UpdateWindow'), 'int', ['pointer']);
var GetWindowThreadProcessId = new NativeFunction(u32.findExportByName('GetWindowThreadProcessId'), 'uint', ['pointer', 'pointer']);
var myPid = Process.id;
var done = {};

function showAll(tag){
  var n = 0;
  var cb = new NativeCallback(function(h, l){
    var p = Memory.alloc(4); GetWindowThreadProcessId(h, p);
    if (p.readU32() !== myPid) return 1;
    var b = Memory.alloc(256); var k = GetClassNameW(h, b, 200);
    var cls = k > 0 ? b.readUtf16String(k) : '';
    if (cls.indexOf('ThunderRT6Form') !== 0) return 1;
    var key = h.toString();
    if (done[key]) return 1;
    done[key] = 1;
    var tb = Memory.alloc(256); var tn = GetWindowTextW(h, tb, 200);
    var title = tn > 0 ? tb.readUtf16String(tn) : '';
    try {
      var st = SetWindowLongW(h, -16, 0);
      SetWindowLongW(h, -16, (st | 0x10000000) & 0xFFFFFFFF);
      var prev = ShowWindow(h, 5);
      UpdateWindow(h);
      emit('[' + tag + '] show ' + h + ' title=' + JSON.stringify(title) + ' prev=' + prev + ' vis=' + IsWindowVisible(h));
      n++;
    } catch (e) { emit('show err ' + e); }
    return 1;
  }, 'int', ['pointer', 'pointer']);
  EnumWindows(cb, ptr(0));
  return n;
}

Interceptor.attach(k32.findExportByName('WaitForMultipleObjects'), {
  onEnter: function(a){
    if (Date.now() - t0 < 2000) return;
    showAll('wait');
  }
});
Interceptor.attach(k32.findExportByName('WaitForSingleObject'), {
  onEnter: function(a){
    if (Date.now() - t0 < 2000) return;
    showAll('wait1');
  }
});
emit('diag97 ready');
