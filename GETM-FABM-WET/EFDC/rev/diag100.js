'use strict';
// diag100.js — 找出主线程长等待的句柄类型
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }

var k32 = Process.findModuleByName('kernel32.dll');
var GetThreadId = new NativeFunction(k32.findExportByName('GetThreadId'), 'uint', ['pointer']);
var GetProcessId = new NativeFunction(k32.findExportByName('GetProcessId'), 'uint', ['pointer']);
var WaitForSingleObject = new NativeFunction(k32.findExportByName('WaitForSingleObject'), 'uint', ['pointer', 'uint']);

function describe(h){
  var s = 'h=' + h;
  try { var tid = GetThreadId(h); if (tid) s += ' THREAD(tid=' + tid + ')'; } catch (e) {}
  try { var pid = GetProcessId(h); if (pid) s += ' PROCESS(pid=' + pid + ')'; } catch (e) {}
  try { var r = WaitForSingleObject(h, 0); s += ' wait0=' + r; } catch (e) { s += ' wait0=?'; }
  return s;
}

function hook(n, cntIdx, hArrIdx, toIdx){
  var p = k32.findExportByName(n);
  if (!p) return;
  Interceptor.attach(p, {
    onEnter: function(a){
      this.t = Date.now(); this.n = n;
      var cnt = a[cntIdx].toInt32();
      this.desc = 'count=' + cnt + ' timeout=' + a[toIdx].toInt32();
      var hs = [];
      try { for (var i = 0; i < Math.min(cnt, 4); i++) hs.push(a[hArrIdx].add(i * 4).readPointer()); } catch (e) {}
      this.hs = hs;
      this.chain = null;
    },
    onLeave: function(r){
      var dt = Date.now() - this.t;
      if (dt < 1000) return;
      var parts = [];
      for (var i = 0; i < this.hs.length; i++) parts.push(describe(this.hs[i]));
      emit(this.n + ' ' + dt + 'ms ret=' + (r.toInt32() >>> 0) + ' ' + this.desc + ' | ' + parts.join(' ; ') + ' | from ' + mod(this.returnAddress));
    }
  });
}
hook('WaitForMultipleObjects', 0, 1, 3);
hook('WaitForMultipleObjectsEx', 0, 1, 2);
emit('diag100 ready');
