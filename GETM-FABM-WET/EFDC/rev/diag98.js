'use strict';
// diag98.js — 贴窗 + 还原 + 置顶 + 强制重绘，并枚举子控件
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }

var k32 = Process.findModuleByName('kernel32.dll');
var u32 = Process.findModuleByName('user32.dll');
var EnumWindows = new NativeFunction(u32.findExportByName('EnumWindows'), 'int', ['pointer', 'pointer']);
var EnumChildWindows = new NativeFunction(u32.findExportByName('EnumChildWindows'), 'int', ['pointer', 'pointer', 'pointer']);
var GetClassNameW = new NativeFunction(u32.findExportByName('GetClassNameW'), 'int', ['pointer', 'pointer', 'int']);
var GetWindowTextW = new NativeFunction(u32.findExportByName('GetWindowTextW'), 'int', ['pointer', 'pointer', 'int']);
var IsWindowVisible = new NativeFunction(u32.findExportByName('IsWindowVisible'), 'int', ['pointer']);
var ShowWindow = new NativeFunction(u32.findExportByName('ShowWindow'), 'int', ['pointer', 'int']);
var SetWindowLongW = new NativeFunction(u32.findExportByName('SetWindowLongW'), 'int', ['pointer', 'int', 'int']);
var SetWindowPos = new NativeFunction(u32.findExportByName('SetWindowPos'), 'int', ['pointer', 'pointer', 'int', 'int', 'int', 'int', 'uint']);
var RedrawWindow = new NativeFunction(u32.findExportByName('RedrawWindow'), 'int', ['pointer', 'pointer', 'pointer', 'uint']);
var UpdateWindow = new NativeFunction(u32.findExportByName('UpdateWindow'), 'int', ['pointer']);
var GetWindowThreadProcessId = new NativeFunction(u32.findExportByName('GetWindowThreadProcessId'), 'uint', ['pointer', 'pointer']);
var GetWindowLongW = new NativeFunction(u32.findExportByName('GetWindowLongW'), 'int', ['pointer', 'int']);
var PeekMessageW = new NativeFunction(u32.findExportByName('PeekMessageW'), 'int', ['pointer','pointer','uint','uint','uint']);
var TranslateMessage = new NativeFunction(u32.findExportByName('TranslateMessage'), 'int', ['pointer']);
var DispatchMessageW = new NativeFunction(u32.findExportByName('DispatchMessageW'), 'int', ['pointer']);
var myPid = Process.id;
var done = {};

function children(h){
  var out = [];
  var cb = new NativeCallback(function(ch, l){
    var b = Memory.alloc(256); var n = GetClassNameW(ch, b, 200);
    var cls = n > 0 ? b.readUtf16String(n) : '';
    out.push(cls);
    return 1;
  }, 'int', ['pointer', 'pointer']);
  EnumChildWindows(h, cb, ptr(0));
  return out;
}

function showAll(tag){
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
    var style = GetWindowLongW(h, -16) | 0;
    emit('BEFORE hwnd=' + h + ' title=' + JSON.stringify(title) + ' style=0x' + (style >>> 0).toString(16) + ' vis=' + IsWindowVisible(h));
    try {
      SetWindowLongW(h, -16, (style | 0x10000000) & 0xFFFFFFFF);
      ShowWindow(h, 9);            // SW_RESTORE
      ShowWindow(h, 5);            // SW_SHOW
      SetWindowPos(h, ptr(-1), 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0040); // NOSIZE|NOMOVE|SHOWWINDOW
      RedrawWindow(h, ptr(0), ptr(0), 0x0001 | 0x0100 | 0x0400);       // INVALIDATE|UPDATENOW|ALLCHILDREN
      UpdateWindow(h);
      emit('AFTER  vis=' + IsWindowVisible(h) + ' style=0x' + (GetWindowLongW(h, -16) >>> 0).toString(16));
      var msg = Memory.alloc(64);
      var end = Date.now() + 250;
      while (Date.now() < end) { if (PeekMessageW(msg, ptr(0), 0, 0, 1) === 0) break; TranslateMessage(msg); DispatchMessageW(msg); }
      var ch = children(h);
      emit('children(' + ch.length + '): ' + ch.slice(0, 25).join(','));
    } catch (e) { emit('err ' + e); }
    return 1;
  }, 'int', ['pointer', 'pointer']);
  EnumWindows(cb, ptr(0));
}

Interceptor.attach(k32.findExportByName('WaitForMultipleObjects'), { onEnter: function(){ if (Date.now()-t0 > 1500) showAll('w'); } });
Interceptor.attach(k32.findExportByName('WaitForSingleObject'), { onEnter: function(){ if (Date.now()-t0 > 1500) showAll('w1'); } });
emit('diag98 ready');


