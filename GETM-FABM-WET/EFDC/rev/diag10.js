'use strict';
// diag10.js — 运行时定位对象表与窗体名映射
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function hex32(v){ return ('00000000'+v.toString(16)).slice(-8); }

function dump(addr, n){
  var out = [];
  for (var i=0;i<n;i++){
    try{ out.push(hex32(addr.add(i*4).readU32())); }catch(e){ out.push('??'); }
  }
  return out.join(' ');
}

setTimeout(function(){
  emit('--- ProjectData @0x4547D0 ---');
  emit(dump(ptr(0x4547D0), 12));
  emit('--- ObjectTable? @0x4DD8A0 ---');
  for (var k=0;k<6;k++){
    emit(' [' + (k*16) + '] ' + dump(ptr(0x4DD8A0 + k*16), 4));
  }
  // 全内存扫 "frmEFDC_Explorer"（UTF-16）与 "frmEFDC_Run"
  var targets = ['frmEFDC_Explorer', 'frmEFDC_Run'];
  var ranges = Process.enumerateRanges('r--');
  for (var t=0;t<targets.length;t++){
    var pat = null;
    try{ pat = Memory.allocUtf16String(targets[t]); }catch(e){ continue; }
    var found = 0;
    for (var i=0;i<ranges.length && found<3;i++){
      var r = ranges[i];
      if (r.size > 200*1024*1024) continue;
      var res = null;
      try{ res = Memory.scanSync(r.base, r.size, targets[t].split('').map(function(c){ return c.charCodeAt(0).toString(16).padStart(2,'0')+'00'; }).join(' ')); }catch(e){ continue; }
      for (var j=0;j<res.length && found<3;j++){
        var a = res[j].address;
        found++;
        emit('HIT ' + targets[t] + ' @ ' + a + '  before: ' + dump(a.sub(32), 8) + '  after: ' + dump(a.add(targets[t].length*2), 8));
      }
    }
    emit('total hits ' + targets[t] + ' = ' + found + ' (scanned ' + ranges.length + ' ranges)');
  }
}, 5000);
emit('diag10 armed');
