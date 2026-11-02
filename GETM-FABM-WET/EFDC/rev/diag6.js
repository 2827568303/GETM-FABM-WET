'use strict';
// diag6.js — 抓真实 HTTP 请求（直接在 socket 层抓明文）
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }
var seen = {};

function dump(buf, len, tag, ra){
  try{
    var n = Math.min(len, 900);
    var arr = new Uint8Array(buf.readByteArray(n));
    var s = '';
    for (var i=0;i<arr.length;i++){
      var c = arr[i];
      s += (c>=32 && c<127) ? String.fromCharCode(c) : (c===13?'\\r':(c===10?'\\n':'.'));
    }
    var key = s.slice(0, 120);
    if (seen[key]) return;
    seen[key] = 1;
    emit(tag + ' [' + len + 'B] from ' + ra + ': ' + s);
  }catch(e){ emit(tag+' dump err '+e); }
}

var ws2 = Process.findModuleByName('ws2_32.dll');
if (ws2) {
  var pSend = ws2.findExportByName('send');
  Interceptor.attach(pSend, { onEnter: function(a){ dump(a[1], a[2].toInt32(), 'SEND', mod(this.returnAddress)); } });
  var pWSASend = ws2.findExportByName('WSASend');
  if (pWSASend) Interceptor.attach(pWSASend, { onEnter: function(a){ dump(a[1].readPointer(), a[2].toInt32(), 'WSASEND', mod(this.returnAddress)); } });
}
emit('diag6 ready');
