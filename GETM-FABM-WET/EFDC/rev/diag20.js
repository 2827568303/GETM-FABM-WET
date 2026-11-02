'use strict';
// diag20.js — 抓 SoftModalMessageBox 的参数与文案，并列出当时的窗口
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function w(p){ try{ return p.isNull()?'':p.readUtf16String(); }catch(e){ return '<bad>'; } }
function dw(p, off){ try{ return p.add(off).readU32() >>> 0; }catch(e){ return -1; } }
function hx(v){ return ('00000000'+(v>>>0).toString(16)).slice(-8); }

var u32 = Process.findModuleByName('user32.dll');
var EnumWindows = new NativeFunction(u32.findExportByName('EnumWindows'), 'int', ['pointer', 'pointer']);
var GetClassNameW = new NativeFunction(u32.findExportByName('GetClassNameW'), 'int', ['pointer', 'pointer', 'int']);
var GetWindowTextW = new NativeFunction(u32.findExportByName('GetWindowTextW'), 'int', ['pointer', 'pointer', 'int']);
var IsWindowVisible = new NativeFunction(u32.findExportByName('IsWindowVisible'), 'int', ['pointer']);
var EnumChildWindows = new NativeFunction(u32.findExportByName('EnumChildWindows'), 'int', ['pointer', 'pointer', 'pointer']);

function listWindows(){
  var out = [];
  var cb = new NativeCallback(function(h, l){
    var buf = Memory.alloc(512);
    var n = GetClassNameW(h, buf, 200);
    var cls = n > 0 ? buf.readUtf16String(n) : '';
    var tb = Memory.alloc(512);
    var tn = GetWindowTextW(h, tb, 200);
    var title = tn > 0 ? tb.readUtf16String(tn) : '';
    var kids = [];
    if (cls === '#32770') {
      var cb2 = new NativeCallback(function(ch, l2){
        var c2 = Memory.alloc(512);
        var n2 = GetClassNameW(ch, c2, 200);
        var cl = n2 > 0 ? c2.readUtf16String(n2) : '';
        var t2 = Memory.alloc(512);
        var tn2 = GetWindowTextW(ch, t2, 400);
        var tx = tn2 > 0 ? t2.readUtf16String(tn2) : '';
        if (tx) kids.push(cl + ':' + JSON.stringify(tx));
        return 1;
      }, 'int', ['pointer', 'pointer']);
      EnumChildWindows(h, cb2, ptr(0));
    }
    out.push(cls + '|' + JSON.stringify(title) + '|vis=' + IsWindowVisible(h) + '|' + h + (kids.length ? ' >> ' + kids.join(' / ') : ''));
    return 1;
  }, 'int', ['pointer', 'pointer']);
  EnumWindows(cb, ptr(0));
  return out;
}

var pSoft = u32.findExportByName('SoftModalMessageBox');
Interceptor.attach(pSoft, { onEnter: function(a){
  var p = a[0];
  emit('SoftModalMessageBox(ptr=' + p + ')');
  var words = [];
  for (var i = 0; i < 16; i++) words.push(hx(dw(p, i * 4)));
  emit('  struct: ' + words.join(' '));
  // 常见布局：+0 cbSize, +4 hwndOwner, +8 hText, +0xC hCaption ...
  for (var off = 4; off <= 0x20; off += 4) {
    var v = dw(p, off);
    if (v > 0x10000) {
      var s = w(ptr(v));
      if (s && s.length >= 2) emit('  [' + ('0x' + off.toString(16)) + '] -> ' + JSON.stringify(s));
    }
  }
  var ws = listWindows();
  emit('  windows now: ' + (ws.length ? ws.join(' ;; ') : '<none>'));
  setTimeout(function(){ var w2 = listWindows(); emit('  +800ms windows: ' + (w2.length ? w2.join(' ;; ') : '<none>')); }, 800);
}});
emit('diag20 ready');
