'use strict';
// diag9.js — 追踪 DSILIC 的加载/实例化路径（文件、LdrLoadDll、所有 CoCreate* 变体）
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }
function w(p){ try{ return p.isNull()?'':p.readUtf16String(); }catch(e){ return '<bad>'; } }
function a(p){ try{ return p.isNull()?'':p.readAnsiString(); }catch(e){ return '<bad>'; } }
function hexg(p){ try{ var u=new Uint8Array(p.readByteArray(16)); return Array.from(u).map(function(x){return x.toString(16).padStart(2,'0');}).join(''); }catch(e){ return '?'; } }

function hook(dll, name, onEnter){
  var m = Process.findModuleByName(dll); if(!m) return;
  var p = m.findExportByName(name); if(!p) return;
  Interceptor.attach(p, { onEnter: function(args){ try{ onEnter(args, this); }catch(e){ emit(name+' ERR '+e); } } });
}

hook('kernel32.dll','CreateFileW', function(args, self){
  var f = w(args[0]);
  if (/DSILIC|shim|Flexnet/i.test(f)) emit('CreateFileW ' + f + ' from ' + mod(self.returnAddress));
});

hook('ntdll.dll','LdrLoadDll', function(args, self){
  emit('LdrLoadDll ' + w(args[2]) + ' from ' + mod(self.returnAddress));
});

hook('ole32.dll','CoCreateInstance', function(args, self){ emit('CoCreateInstance ' + hexg(args[0]) + ' from ' + mod(self.returnAddress)); });
hook('ole32.dll','CoCreateInstanceEx', function(args, self){ emit('CoCreateInstanceEx ' + hexg(args[0]) + ' from ' + mod(self.returnAddress)); });
hook('ole32.dll','CoGetClassObject', function(args, self){ emit('CoGetClassObject ' + hexg(args[0]) + ' from ' + mod(self.returnAddress)); });
hook('ole32.dll','CLSIDFromProgID', function(args, self){ emit('CLSIDFromProgID "' + w(args[0]) + '" from ' + mod(self.returnAddress)); });
hook('ole32.dll','CLSIDFromProgIDEx', function(args, self){ emit('CLSIDFromProgIDEx "' + w(args[0]) + '"'); });
hook('ole32.dll','ProgIDFromCLSID', function(args, self){ emit('ProgIDFromCLSID ' + hexg(args[0])); });
hook('oleaut32.dll','LoadTypeLib', function(args, self){ emit('LoadTypeLib "' + w(args[0]) + '"'); });
hook('oleaut32.dll','LoadTypeLibEx', function(args, self){ emit('LoadTypeLibEx "' + w(args[0]) + '"'); });
hook('oleaut32.dll','OleLoadPictureEx', function(args, self){ emit('OleLoadPictureEx'); });
emit('diag9 ready');
