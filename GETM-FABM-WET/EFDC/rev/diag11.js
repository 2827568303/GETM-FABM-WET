'use strict';
// diag11.js — 运行时读取每个窗体记录的 +8 字段（应被填成 class info）
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function hx(v){ return ('00000000'+v.toString(16)).slice(-8); }
function dw(a){ try{ return a.readU32(); }catch(e){ return -1; } }
function dump(base, n){
  var out=[];
  for(var i=0;i<n;i++) out.push(hx(ptr(base).add(i*4).readU32() >>> 0));
  return out.join(' ');
}

setTimeout(function(){
  var recs = {
    'frmAct_ExpirationAlerts': 0x4DD90C,
    'frmAct_License_Validation': 0x4DD93C,
    'frmActivation': null,
    'frmEFDC_Explorer': 0x4DF88C,
    'frmEFDC_Explorer_TitleForm': 0x4DEDAC
  };
  for (var k in recs) {
    if (!recs[k]) continue;
    var r = ptr(recs[k]);
    var p8 = r.add(8).readU32() >>> 0;
    var line = k + ' rec=' + hx(recs[k]) + ' +8=' + hx(p8);
    if (p8 > 0x400000 && p8 < 0x1620000) {
      line += '  [p8+4]=' + hx(ptr(p8).add(4).readU32() >>> 0);
      line += '  p8: ' + dump(p8, 10);
    }
    emit(line);
  }
  emit('objtbl head: ' + dump(0x4DD8A0, 12));
}, 4000);
emit('diag11 armed');
