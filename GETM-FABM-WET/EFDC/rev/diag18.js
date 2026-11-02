'use strict';
// diag18.js — CheckLicensing 期间对全线程 EIP 采样，定位真实停留点
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function key(a){
  try{ var m=Process.findModuleByAddress(a); return m ? (m.name+'+0x'+a.sub(m.base).toString(16)) : ('unk@'+a.toString()); }
  catch(e){ return '?'; }
}

var inside = false;
Interceptor.attach(ptr(0x81C4C0), {
  onEnter: function(){ inside = true; emit('ENTER CheckLicensing'); },
  onLeave: function(r){ inside = false; emit('LEAVE CheckLicensing ret=' + r.toInt32()); }
});

var hist = {};
var iv = setInterval(function(){
  try {
    var ths = Process.enumerateThreads();
    for (var i = 0; i < ths.length; i++) {
      var c = ths[i].context;
      if (!c || !c.pc) continue;
      var k = key(c.pc);
      hist[k] = (hist[k] || 0) + 1;
    }
  } catch (e) {}
}, 300);

setTimeout(function(){
  clearInterval(iv);
  var arr = Object.keys(hist).map(function(k){ return [k, hist[k]]; });
  arr.sort(function(a,b){ return b[1]-a[1]; });
  emit('--- EIP 采样 top 20 (inside=' + inside + ') ---');
  for (var i = 0; i < Math.min(20, arr.length); i++) emit('  ' + arr[i][1] + '  ' + arr[i][0]);
}, 14000);
emit('diag18 ready');
