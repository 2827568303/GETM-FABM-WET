'use strict';
// diag4.js — 单实例互斥体 / 等待点诊断
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }
function w(p){ try{ return p.isNull()?'':p.readUtf16String(); }catch(e){ return '<bad>'; } }

function hookFn(dll, name, onEnter){
  var m = Process.findModuleByName(dll); if(!m) return null;
  var p = m.findExportByName(name); if(!p) return null;
  Interceptor.attach(p, { onEnter: function(a){ try{ onEnter(a, this); }catch(e){ emit(name+' ERR '+e); } } });
  return p;
}

hookFn('kernel32.dll','CreateMutexW', function(a,self){ emit('CreateMutex name='+JSON.stringify(w(a[2]))+' from '+mod(self.returnAddress)); });
hookFn('kernel32.dll','OpenMutexW', function(a,self){ emit('OpenMutex name='+JSON.stringify(w(a[2]))+' from '+mod(self.returnAddress)); });
hookFn('kernel32.dll','CreateEventW', function(a,self){ emit('CreateEvent name='+JSON.stringify(w(a[3]))+' from '+mod(self.returnAddress)); });
hookFn('kernel32.dll','OpenEventW', function(a,self){ emit('OpenEvent name='+JSON.stringify(w(a[2]))+' from '+mod(self.returnAddress)); });
hookFn('kernel32.dll','CreateSemaphoreW', function(a,self){ emit('CreateSemaphore name='+JSON.stringify(w(a[2]))+' from '+mod(self.returnAddress)); });

var waitStart = {};
hookFn('kernel32.dll','WaitForSingleObject', function(a,self){
  var ms = a[1].toInt32();
  if (ms === -1 || ms > 1000) emit('WaitForSingleObject(h='+a[0]+', ms='+ms+') from '+mod(self.returnAddress));
});
hookFn('kernel32.dll','WaitForSingleObjectEx', function(a,self){
  var ms = a[1].toInt32();
  if (ms === -1 || ms > 1000) emit('WaitForSingleObjectEx(h='+a[0]+', ms='+ms+') from '+mod(self.returnAddress));
});
// VB6 声明的同名 API 直接走 IAT，钩 IAT 目标即可（同上，kernel32 导出即同一函数）

hookFn('user32.dll','MessageBoxW', function(a,self){ emit('MSGBOX '+JSON.stringify(w(a[1]))+' | '+JSON.stringify(w(a[2]))); });

// 窗口创建（VB6 窗体）
hookFn('user32.dll','CreateWindowExW', function(a,self){
  var cls = w(a[1]);
  if (/ThunderRT6|MDIForm/i.test(cls)) emit('CreateWindow cls='+cls+' title='+JSON.stringify(w(a[2]))+' style=0x'+(a[3].toUInt32()>>>0).toString(16)+' from '+mod(self.returnAddress));
});
emit('diag4 ready');
