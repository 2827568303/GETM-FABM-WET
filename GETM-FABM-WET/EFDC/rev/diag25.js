'use strict';
// diag25.js — 抓 rtcMsgBox 的调用点（app 侧），用于定位"licenseWrapper is not valid"分支
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }
function bs(p){ try{ return p.isNull()?'':p.readUtf16String(); }catch(e){ return '<bad>'; } }

var vb = Process.findModuleByName('MSVBVM60.DLL');
['rtcMsgBox','rtcMsgBoxVar','__vbaMsgBox'].forEach(function(n){
  var p = vb.findExportByName(n);
  if(!p){ emit('no ' + n); return; }
  Interceptor.attach(p, { onEnter: function(a){
    emit(n + ' caller=' + mod(this.returnAddress) + ' text=' + JSON.stringify(bs(a[0])));
  }});
  emit('hooked ' + n);
});
emit('diag25 ready');
