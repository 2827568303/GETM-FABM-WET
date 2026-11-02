'use strict';
// diag13.js — 在主线程的 TitleInit 入口，抢先创建主窗体并把全局对象指针填好
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }
function hx(v){ return ('00000000'+(v>>>0).toString(16)).slice(-8); }

var vb = Process.findModuleByName('MSVBVM60.DLL');
var pNew2 = vb.findExportByName('__vbaNew2');
var New2 = new NativeFunction(pNew2, 'void', ['pointer', 'pointer', 'pointer']);

var GLOB = ptr(0x16249B0);
var CANDIDATES = [0x482C3C];
var done = false;

Interceptor.attach(ptr(0x156ACC0), { onEnter: function(){
  if (done) return;
  done = true;
  emit('ENTER TitleInit — 注入创建窗体');
  for (var i = 0; i < CANDIDATES.length; i++) {
    var ci = ptr(CANDIDATES[i]);
    var out = Memory.alloc(4);
    try {
      New2(ci, out, ptr(0));
      var obj = out.readPointer();
      emit('  __vbaNew2(' + ci + ') -> obj=' + obj + ' [ci+4]=' + hx(ci.add(4).readU32()));
      if (!obj.isNull()) {
        var vt = obj.readPointer();
        emit('  vtable=' + vt);
        GLOB.writePointer(obj);
        emit('  [0x16249b0] 已写入 ' + obj);
      }
    } catch (e) { emit('  New2 异常 ' + e); }
  }
}});

var u32 = Process.findModuleByName('user32.dll');
var pCreate = u32.findExportByName('CreateWindowExW');
Interceptor.attach(pCreate, { onEnter: function(a){
  try{
    var cls = a[1].readUtf16String();
    if (/ThunderRT6/.test(cls)) emit('CreateWindow cls=' + cls + ' title=' + JSON.stringify(a[2].isNull() ? '' : a[2].readUtf16String()) + ' style=' + hx(a[3].toUInt32()));
  }catch(e){}
}});

var pShow = u32.findExportByName('ShowWindow');
Interceptor.attach(pShow, { onEnter: function(a){ emit('ShowWindow hwnd=' + a[0] + ' cmd=' + a[1].toInt32() + ' from ' + mod(this.returnAddress)); }});
emit('diag13 ready');
