'use strict';
// diag39.js — 在进程退出前检查窗体是否还在；若在，强制显示并接管消息循环
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }

var u32 = Process.findModuleByName('user32.dll');
var EnumWindows = new NativeFunction(u32.findExportByName('EnumWindows'), 'int', ['pointer', 'pointer']);
var GetClassNameW = new NativeFunction(u32.findExportByName('GetClassNameW'), 'int', ['pointer', 'pointer', 'int']);
var GetWindowTextW = new NativeFunction(u32.findExportByName('GetWindowTextW'), 'int', ['pointer', 'pointer', 'int']);
var IsWindowVisible = new NativeFunction(u32.findExportByName('IsWindowVisible'), 'int', ['pointer']);
var ShowWindow = new NativeFunction(u32.findExportByName('ShowWindow'), 'int', ['pointer', 'int']);
var GetWindowThreadProcessId = new NativeFunction(u32.findExportByName('GetWindowThreadProcessId'), 'uint', ['pointer', 'pointer']);
var GetMessageW = new NativeFunction(u32.findExportByName('GetMessageW'), 'int', ['pointer', 'pointer', 'uint', 'uint']);
var TranslateMessage = new NativeFunction(u32.findExportByName('TranslateMessage'), 'int', ['pointer']);
var DispatchMessageW = new NativeFunction(u32.findExportByName('DispatchMessageW'), 'int', ['pointer']);

var myPid = Process.id;

function listWindows(tag){
  var out = [];
  var cb = new NativeCallback(function(h, l){
    var pidBuf = Memory.alloc(4);
    GetWindowThreadProcessId(h, pidBuf);
    if (pidBuf.readU32() === myPid) {
      var b = Memory.alloc(512);
      var n = GetClassNameW(h, b, 200);
      var cls = n > 0 ? b.readUtf16String(n) : '';
      var tb = Memory.alloc(512);
      var tn = GetWindowTextW(h, tb, 200);
      var title = tn > 0 ? tb.readUtf16String(tn) : '';
      out.push(cls + '|' + JSON.stringify(title) + '|vis=' + IsWindowVisible(h) + '|' + h);
    }
    return 1;
  }, 'int', ['pointer', 'pointer']);
  EnumWindows(cb, ptr(0));
  emit(tag + ': ' + (out.length ? out.join(' ;; ') : '<none>'));
  return out;
}

var nt = Process.findModuleByName('ntdll.dll');
Interceptor.attach(nt.findExportByName('RtlExitUserProcess'), { onEnter: function(a){
  emit('RtlExitUserProcess(' + a[0].toInt32() + ')');
  var ws = listWindows('  退出时的窗口');
  var shown = 0;
  var cb = new NativeCallback(function(h, l){
    var pidBuf = Memory.alloc(4);
    GetWindowThreadProcessId(h, pidBuf);
    if (pidBuf.readU32() === myPid) {
      var b = Memory.alloc(512);
      var n = GetClassNameW(h, b, 200);
      var cls = n > 0 ? b.readUtf16String(n) : '';
      if (cls.indexOf('ThunderRT6Form') === 0) {
        ShowWindow(h, 5);
        shown++;
        emit('  forced show ' + h + ' now vis=' + IsWindowVisible(h));
      }
    }
    return 1;
  }, 'int', ['pointer', 'pointer']);
  EnumWindows(cb, ptr(0));
  if (shown > 0) {
    emit('进入自建消息循环（阻止退出）');
    var msg = Memory.alloc(64);
    while (true) {
      var r = GetMessageW(msg, ptr(0), 0, 0);
      if (r <= 0) break;
      TranslateMessage(msg);
      DispatchMessageW(msg);
    }
    emit('消息循环结束');
  }
}});
emit('diag39 ready');
