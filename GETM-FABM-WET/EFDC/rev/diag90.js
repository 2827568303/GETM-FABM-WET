'use strict';
// diag90.js — 窗体 Load 阻塞窗口（2.5s~9.5s）内的全量活动追踪
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }
function inWin(){ var t=Date.now()-t0; return t>=2400 && t<=9600; }

function hook(dll, name, builder){
  var m = Process.findModuleByName(dll);
  if (!m) { emit('no module '+dll); return; }
  var p = m.findExportByName(name);
  if (!p) { emit('no export '+name); return; }
  Interceptor.attach(p, { onEnter: function(a){ if(!inWin()) return; try{ var s=builder(a,this); if(s) emit(s); }catch(e){} } });
}

hook('kernel32.dll','Sleep', function(a){ return 'Sleep('+a[0].toInt32()+') from '+mod(this.returnAddress); });
hook('kernel32.dll','WaitForSingleObject', function(a){ return 'Wait(h='+a[0]+',ms='+a[1].toInt32()+') from '+mod(this.returnAddress); });
hook('kernel32.dll','WaitForSingleObjectEx', function(a){ return 'WaitEx(h='+a[0]+',ms='+a[1].toInt32()+') from '+mod(this.returnAddress); });
hook('kernel32.dll','CreateFileW', function(a){ var f=a[0].readUtf16String(); return 'Open '+f; });
hook('kernel32.dll','LoadLibraryExW', function(a){ return 'LoadLib '+a[0].readUtf16String(); });
hook('advapi32.dll','RegOpenKeyExW', function(a){ return 'RegOpen '+(a[1].isNull()?'':a[1].readUtf16String()); });
hook('winhttp.dll','WinHttpSendRequest', function(a){ return 'WinHttpSend'; });
hook('winhttp.dll','WinHttpConnect', function(a){ return 'WinHttpConnect '+a[1].readUtf16String(); });
hook('winhttp.dll','WinHttpReceiveResponse', function(a){ return 'WinHttpRecv'; });
hook('wininet.dll','InternetOpenUrlW', function(a){ return 'InetOpen '+a[1].readUtf16String(); });
hook('ws2_32.dll','connect', function(a){ return 'connect()'; });
emit('diag90 ready');
