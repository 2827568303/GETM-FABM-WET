'use strict';
// diag23.js — 抓 VB6 运行时抛错点（用于定位 481 的来源）
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }
function trace(ctx, n){ try{ return Thread.backtrace(ctx, Backtracer.ACCURATE).slice(0, n||12).map(mod).join(' <- '); }catch(e){ return '?'; } }
function ftrace(ctx, n){ try{ return Thread.backtrace(ctx, Backtracer.FUZZY).slice(0, n||16).map(mod).join(' <- '); }catch(e){ return '?'; } }

var k32 = Process.findModuleByName('kernel32.dll');
Interceptor.attach(k32.findExportByName('RaiseException'), {
  onEnter: function(a){
    var code = a[0].toUInt32() >>> 0;
    if (code === 0xE06D7363) return;
    emit('RaiseException code=0x' + code.toString(16) + ' from ' + mod(this.returnAddress));
    emit('  accurate: ' + trace(this.context, 10));
    emit('  fuzzy   : ' + ftrace(this.context, 16));
  }
});
emit('diag23 ready');
