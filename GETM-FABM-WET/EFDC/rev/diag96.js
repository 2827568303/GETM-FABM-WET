'use strict';
// diag96.js — Show 之后（2s~10s）找出耗时 >400ms 的阻塞调用
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }
function ftrace(ctx,n){ try{ return Thread.backtrace(ctx, Backtracer.FUZZY).slice(0,n||12).map(mod).join(' <- '); }catch(e){ return '?'; } }

function hookDur(dll, name, minMs){
  var m = Process.findModuleByName(dll);
  if (!m) return false;
  var p = m.findExportByName(name);
  if (!p) return false;
  Interceptor.attach(p, {
    onEnter: function(a){ this.t = Date.now(); this.chain = ftrace(this.context, 12); },
    onLeave: function(r){
      var dt = Date.now() - this.t;
      var now = Date.now() - t0;
      if (now > 1800 && dt >= (minMs||400)) emit(name+' '+dt+'ms ret='+(r.toInt32()>>>0)+'  '+this.chain);
    }
  });
  return true;
}

['kernel32.dll','wininet.dll','winhttp.dll','ws2_32.dll','ole32.dll','combase.dll'].forEach(function(dll){
  ['WaitForSingleObject','WaitForSingleObjectEx','Sleep','MsgWaitForMultipleObjects','MsgWaitForMultipleObjectsEx',
   'WaitForMultipleObjects','InternetReadFile','HttpSendRequestW','InternetConnectW','InternetOpenUrlW',
   'WinHttpReceiveResponse','WinHttpSendRequest','recv','CoWaitForMultipleHandles','InternetQueryDataAvailable'].forEach(function(n){
    hookDur(dll, n, 400);
  });
});

var vb = Process.findModuleByName('MSVBVM60.DLL');
try {
  var p = vb.findExportByName('__vbaFileOpen');
  Interceptor.attach(p, { onEnter: function(a){ if (Date.now()-t0 > 1800) { try{ emit('FileOpen '+(a[3].isNull()?'':a[3].readUtf16String())); }catch(e){} } } });
} catch (e) {}
emit('diag96 ready');
