'use strict';
// diag36.js — 跳过 CheckLicensing 后，追踪流程去向
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }

Interceptor.replace(ptr(0x81C4C0), new NativeCallback(function(){ emit('skip CheckLicensing'); }, 'void', []));

['0x81BBA0','0x828F50','0x156ACC0','0x156AD3B'].forEach(function(a){
  try {
    Interceptor.attach(ptr(parseInt(a, 16)), {
      onEnter: function(){ emit('ENTER ' + a); },
      onLeave: function(r){ emit('LEAVE ' + a + ' ret=' + r.toInt32()); }
    });
  } catch (e) { emit('attach fail ' + a); }
});

var hist = {};
var iv = setInterval(function(){
  try {
    var ths = Process.enumerateThreads();
    for (var i = 0; i < ths.length; i++) {
      var c = ths[i].context;
      if (!c || !c.pc) continue;
      var k = mod(c.pc);
      hist[k] = (hist[k] || 0) + 1;
    }
  } catch (e) {}
}, 300);
setTimeout(function(){
  clearInterval(iv);
  var arr = Object.keys(hist).map(function(k){ return [k, hist[k]]; });
  arr.sort(function(a,b){ return b[1]-a[1]; });
  emit('--- EIP top ---');
  for (var i = 0; i < Math.min(12, arr.length); i++) emit('  ' + arr[i][1] + '  ' + arr[i][0]);
}, 12000);
emit('diag36 ready');
