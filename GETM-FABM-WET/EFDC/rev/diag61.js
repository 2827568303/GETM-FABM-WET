'use strict';
// diag61.js — 拿到 splash 窗口句柄后向它发消息，试探能否触发 VB 侧回调
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }

var u32 = Process.findModuleByName('user32.dll');
var PostMessageW = new NativeFunction(u32.findExportByName('PostMessageW'), 'int', ['pointer', 'uint', 'pointer', 'pointer']);
var SendMessageW = new NativeFunction(u32.findExportByName('SendMessageW'), 'pointer', ['pointer', 'uint', 'pointer', 'pointer']);
var IsWindowVisible = new NativeFunction(u32.findExportByName('IsWindowVisible'), 'int', ['pointer']);
var EnumWindows = new NativeFunction(u32.findExportByName('EnumWindows'), 'int', ['pointer', 'pointer']);
var GetClassNameW = new NativeFunction(u32.findExportByName('GetClassNameW'), 'int', ['pointer', 'pointer', 'int']);
var GetWindowThreadProcessId = new NativeFunction(u32.findExportByName('GetWindowThreadProcessId'), 'uint', ['pointer', 'pointer']);

var myPid = Process.id;
var splash = null;

Interceptor.attach(u32.findExportByName('CreateWindowExW'), {
  onEnter: function(a){ try{ this.cls = a[1].readUtf16String(); }catch(e){ this.cls=''; } },
  onLeave: function(r){
    if (this.cls && this.cls.indexOf('ThunderRT6Form') === 0 && splash === null) {
      splash = r;
      emit('splash hwnd=' + splash + ' cls=' + this.cls);
      setTimeout(function(){ poke('t+500'); }, 500);
      setTimeout(function(){ poke('t+1500'); }, 1500);
      setTimeout(function(){ poke('t+3000'); }, 3000);
    }
  }
});

function windows(tag){
  var out = [];
  var cb = new NativeCallback(function(h, l){
    var pidBuf = Memory.alloc(4);
    GetWindowThreadProcessId(h, pidBuf);
    if (pidBuf.readU32() === myPid) {
      var b = Memory.alloc(512);
      var n = GetClassNameW(h, b, 200);
      var cls = n > 0 ? b.readUtf16String(n) : '';
      if (cls.indexOf('Thunder') === 0) out.push(cls + '|vis=' + IsWindowVisible(h));
    }
    return 1;
  }, 'int', ['pointer', 'pointer']);
  EnumWindows(cb, ptr(0));
  emit('  [' + tag + '] ' + out.join(' ;; '));
}

function poke(tag){
  if (!splash) return;
  emit('poke ' + tag + ' on ' + splash);
  PostMessageW(splash, 0x0018 /*WM_SHOWWINDOW*/, ptr(1), ptr(0));
  SendMessageW(splash, 0x000F /*WM_PAINT*/, ptr(0), ptr(0));
  PostMessageW(splash, 0x0201 /*WM_LBUTTONDOWN*/, ptr(1), ptr(0x000A000A));
  PostMessageW(splash, 0x0202 /*WM_LBUTTONUP*/, ptr(0), ptr(0x000A000A));
  PostMessageW(splash, 0x0100 /*WM_KEYDOWN*/, ptr(0x0D), ptr(0));
  setTimeout(function(){ windows(tag); }, 800);
}
emit('diag61 ready');
