'use strict';
// diag21.js — 观察启动期窗体创建 + 图片加载全路径
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function hx(v){ return ('00000000'+(v>>>0).toString(16)).slice(-8); }

// 1) 窗体创建点与随后的方法调用
try{ Interceptor.attach(ptr(0x156ABA0), { onEnter: function(){ emit('after __vbaNew2'); } }); }catch(e){ emit('skip 156ABA0'); }
try{ Interceptor.attach(ptr(0x156ABA8), {
  onEnter: function(){ emit('ENTER method[obj+0x1B8]'); },
  onLeave: function(r){ emit('LEAVE method[obj+0x1B8] ret=' + r.toInt32()); }
}); }catch(e){ emit('skip 156ABA8'); }
Interceptor.attach(ptr(0x156AD74), {
  onEnter: function(){ emit('ENTER method[obj+0x250]'); },
  onLeave: function(r){ emit('LEAVE method[obj+0x250]'); }
});

// 2) 图片加载
['OleLoadPicture','OleLoadPictureEx','OleLoadPicturePath'].forEach(function(n){
  var m = Process.findModuleByName('oleaut32.dll');
  if (!m) return;
  var p = m.findExportByName(n);
  if (!p) { emit('no export ' + n); return; }
  Interceptor.attach(p, {
    onEnter: function(a){ this.n = n; },
    onLeave: function(r){ emit(n + ' hr=' + r.toInt32() + ' (0x' + hx(r.toInt32()) + ')'); }
  });
  emit('hooked ' + n);
});

// 3) 消息框（VB6 走 SoftModalMessageBox）
var u32 = Process.findModuleByName('user32.dll');
var pSoft = u32.findExportByName('SoftModalMessageBox');
if (pSoft) Interceptor.attach(pSoft, { onEnter: function(a){
  try{
    var p = a[0];
    var t = p.add(0xC).readPointer();
    var c = p.add(0x10).readPointer();
    emit('SoftModalMessageBox text=' + JSON.stringify(t.isNull()?'':t.readUtf16String()));
  }catch(e){}
}});
emit('diag21 ready');

