'use strict';
// diag106.js — 把主线程的 WaitForMultipleObjects 换成"边等边泵消息"
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }

var k32 = Process.findModuleByName('kernel32.dll');
var u32 = Process.findModuleByName('user32.dll');
var _kbm = Process.findModuleByName('kernelbase.dll');
var WaitForMultipleObjectsOrig = new NativeFunction((_kbm || k32).findExportByName('WaitForMultipleObjects'), 'uint', ['uint', 'pointer', 'int', 'uint']);
var MsgWaitOrig = new NativeFunction(u32.findExportByName('MsgWaitForMultipleObjects'), 'uint', ['uint', 'pointer', 'int', 'uint', 'uint']);
var PeekMessageW = new NativeFunction(u32.findExportByName('PeekMessageW'), 'int', ['pointer', 'pointer', 'uint', 'uint', 'uint']);
var TranslateMessage = new NativeFunction(u32.findExportByName('TranslateMessage'), 'int', ['pointer']);
var DispatchMessageW = new NativeFunction(u32.findExportByName('DispatchMessageW'), 'int', ['pointer']);
var Sleep = new NativeFunction(k32.findExportByName('Sleep'), 'void', ['uint']);

var msg = Memory.alloc(64);
var pumping = 0;

function pump(ms){
  var end = Date.now() + ms;
  pumping++;
  while (Date.now() < end) {
    var got = 0;
    while (PeekMessageW(msg, ptr(0), 0, 0, 1) !== 0) {  // PM_REMOVE
      TranslateMessage(msg);
      DispatchMessageW(msg);
      got++;
      if (got > 64) break;
    }
    Sleep(5);
  }
  pumping--;
}

var kb = Process.findModuleByName('kernelbase.dll');
var addr = kb ? kb.findExportByName('WaitForMultipleObjects') : k32.findExportByName('WaitForMultipleObjects');
Interceptor.replace(addr, new NativeCallback(function(count, handles, waitAll, ms){
  var isMain = (Process.getCurrentThreadId() === Process.id);
  if (isMain && count === 3) {
    // 分片等待 + 泵消息
    var total = (ms === 0xFFFFFFFF) ? 0xFFFFFFFF : ms;
    var elapsed = 0;
    while (elapsed < total) {
      var r = WaitForMultipleObjectsOrig(count, handles, waitAll, 20);
      if (r !== 258) { emit('wait satisfied ret=' + r + ' after ' + elapsed + 'ms'); return r; }
      pump(5);
      elapsed += 25;
      if (total !== 0xFFFFFFFF && elapsed > total) break;
    }
    return 258;
  }
  return WaitForMultipleObjectsOrig(count, handles, waitAll, ms);
}, 'uint', ['uint', 'pointer', 'int', 'uint']));
emit('diag106 ready (main-thread WaitForMultipleObjects replaced by pumping wait)');

