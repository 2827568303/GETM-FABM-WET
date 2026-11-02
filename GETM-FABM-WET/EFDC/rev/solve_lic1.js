'use strict';
// solve_lic1.js — 抓出打印 "WITHOUT LICENSE" 的调用者
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }

var k32 = Process.findModuleByName('kernel32.dll');
function hook(n, bufIdx, lenIdx){
  var p = k32.findExportByName(n);
  if (!p) { emit('no ' + n); return; }
  Interceptor.attach(p, {
    onEnter: function(a){
      try {
        var buf = a[bufIdx], len = a[lenIdx].toInt32();
        if (!buf.isNull() && len > 0 && len < 4096) {
          var b = new Uint8Array(buf.readByteArray(len));
          var s = '';
          for (var i = 0; i < b.length; i++) s += String.fromCharCode(b[i]);
          if ((s.indexOf('LICENSE') >= 0 || s.indexOf('Pause') >= 0)) {
            emit('[' + n + '] ' + JSON.stringify(s.slice(0, 120)));
            emit('   stack: ' + Thread.backtrace(this.context, Backtracer.ACCURATE).slice(0, 12).map(mod).join(' <- '));
          }
        }
      } catch (e) {}
    }
  });
}
hook('WriteConsoleA', 1, 2);
hook('WriteFile', 1, 2);
emit('solve_lic1 ready');


