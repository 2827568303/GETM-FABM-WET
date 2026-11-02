'use strict';
// diag7.js — 定位"真正卡住的系统调用"：统计每次阻塞调用的耗时与调用栈
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }
function bt(ctx){ try{ return Thread.backtrace(ctx, Backtracer.FUZZY).slice(0,9).map(mod).join(' <- '); }catch(e){ return '<bt?>'; } }

function hookSys(name, kind){
  var m = Process.findModuleByName('ntdll.dll'); if(!m) return;
  var p = m.findExportByName(name); if(!p) return;
  Interceptor.attach(p, {
    onEnter: function(a){
      this.t = Date.now();
      this.tid = Process.getCurrentThreadId();
      this.chain = bt(this.context);
      this.a0 = a[0];
    },
    onLeave: function(r){
      var dt = Date.now() - this.t;
      if (dt >= 1500) {
        emit(name + ' ' + dt + 'ms tid=' + this.tid + ' h=' + this.a0 + ' ' + this.chain);
      }
    }
  });
}

hookSys('NtWaitForSingleObject');
hookSys('NtWaitForMultipleObjects');
hookSys('NtDeviceIoControlFile');
hookSys('NtDelayExecution');
hookSys('NtUserGetMessage');
hookSys('NtUserWaitMessage');
hookSys('NtUserPeekMessage');
hookSys('NtRemoveIoCompletion');

// 主线程是谁：VB6 的 Sub Main 在进程主线程
try {
  var k32 = Process.findModuleByName('kernel32.dll');
  var gct = k32.findExportByName('GetCurrentThreadId');
} catch(e){}
emit('diag7 ready');
