'use strict';
// diag13b.js — 在窗体工厂 helper 入口前，用主窗体 class info 抢先创建对象并写入全局
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }
function hx(v){ return ('00000000'+(v>>>0).toString(16)).slice(-8); }

var vb = Process.findModuleByName('MSVBVM60.DLL');
var New2 = new NativeFunction(vb.findExportByName('__vbaNew2'), 'void', ['pointer', 'pointer', 'pointer']);
var GLOB = ptr(0x16249B0);
var CANDIDATES = [0x482C3C, 0x4D5204];
var injected = false;

function tryCreate(ci, tag){
  var out = Memory.alloc(4);
  out.writePointer(ptr(0));
  try{
    New2(ptr(ci), out, ptr(0));
    var obj = out.readPointer();
    emit('  New2(' + tag + ' ' + hx(ci) + ') -> obj=' + obj);
    if (!obj.isNull()) {
      emit('    vtable=' + obj.readPointer());
      return obj;
    }
  }catch(e){ emit('  New2(' + tag + ') 异常 ' + e); }
  return null;
}

Interceptor.attach(ptr(0x156AD3B), { onEnter: function(){
  if (injected) return;
  injected = true;
  var cur = GLOB.readPointer();
  emit('HELPER hit, 当前全局对象=' + cur);
  if (!cur.isNull()) return;
  for (var i=0;i<CANDIDATES.length;i++){
    var obj = tryCreate(CANDIDATES[i], 'cand' + i);
    if (obj && !obj.isNull()) { GLOB.writePointer(obj); emit('  已写入全局 ' + obj); break; }
  }
}});

var u32 = Process.findModuleByName('user32.dll');
Interceptor.attach(u32.findExportByName('CreateWindowExW'), { onEnter: function(a){
  try{ var cls=a[1].readUtf16String(); if(/ThunderRT6/.test(cls)) emit('CreateWindow cls='+cls+' title='+JSON.stringify(a[2].isNull()?'':a[2].readUtf16String())+' style='+hx(a[3].toUInt32())); }catch(e){}
}});
Interceptor.attach(u32.findExportByName('ShowWindow'), { onEnter: function(a){ emit('ShowWindow hwnd='+a[0]+' cmd='+a[1].toInt32()+' from '+mod(this.returnAddress)); }});
emit('diag13b ready');
