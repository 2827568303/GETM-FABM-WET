'use strict';
// diag19.js — 抓 VB6 真正的消息框（MessageBoxTimeout / SoftModalMessageBox 等）
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function w(p){ try{ return p.isNull()?'':p.readUtf16String(); }catch(e){ return '<bad>'; } }
function hook(dll, name, fn){
  var m = Process.findModuleByName(dll); if(!m) return;
  var p = m.findExportByName(name); if(!p) { emit('no export '+dll+'!'+name); return; }
  Interceptor.attach(p, { onEnter: function(a){ try{ fn(a, this); }catch(e){ emit(name+' ERR '+e); } } });
  emit('hooked '+dll+'!'+name+' @'+p);
}

hook('user32.dll','MessageBoxTimeoutW', function(a,self){ emit('MBTW text='+JSON.stringify(w(a[1]))+' cap='+JSON.stringify(w(a[2]))+' from '+self.returnAddress); });
hook('user32.dll','MessageBoxTimeoutA', function(a,self){ emit('MBTA'); });
hook('user32.dll','MessageBoxExW', function(a,self){ emit('MBExW text='+JSON.stringify(w(a[1]))); });
hook('win32u.dll','SoftModalMessageBox', function(a,self){ emit('SoftModalMessageBox'); });
hook('user32.dll','SoftModalMessageBox', function(a,self){ emit('SoftModalMessageBox(u32)'); });
hook('user32.dll','DialogBoxParamW', function(a,self){ emit('DialogBoxParamW'); });
hook('user32.dll','CreateDialogParamW', function(a,self){ emit('CreateDialogParamW'); });
hook('comctl32.dll','TaskDialogIndirect', function(a,self){ emit('TaskDialog'); });

// 同时记录 MessageBoxIndirectW 的完整结构（VB6 常用）
var m = Process.findModuleByName('user32.dll');
var p = m.findExportByName('MessageBoxIndirectW');
if (p) Interceptor.attach(p, { onEnter: function(a){
  try{
    var pms = a[0];
    var txt = pms.add(12).readPointer();
    var cap = pms.add(16).readPointer();
    emit('MBIndirect text='+JSON.stringify(w(txt))+' cap='+JSON.stringify(w(cap)));
  }catch(e){ emit('MBIndirect ERR '+e); }
}});
emit('diag19 ready');
