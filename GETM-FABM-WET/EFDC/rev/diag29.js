'use strict';
// diag29.js — 吞掉弹框，抓住进程退出的调用点（找出 End/ExitProcess 的来源）
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }
function ftrace(ctx, n){ try{ return Thread.backtrace(ctx, Backtracer.FUZZY).slice(0, n||24).map(mod).join(' <- '); }catch(e){ return '?'; } }

var u32 = Process.findModuleByName('user32.dll');
var pSoft = u32.findExportByName('SoftModalMessageBox');
try{
  Interceptor.replace(pSoft, new NativeCallback(function(pms){
    try{
      var t = pms.add(0xC).readPointer();
      emit('swallow msgbox text=' + JSON.stringify(t.isNull()?'':t.readUtf16String()));
    }catch(e){}
    return 1;
  }, 'int', ['pointer']));
  emit('SoftModalMessageBox swallowed');
}catch(e){ emit('replace fail ' + e); }

var k32 = Process.findModuleByName('kernel32.dll');
Interceptor.attach(k32.findExportByName('ExitProcess'), {
  onEnter: function(a){
    emit('ExitProcess(' + a[0].toInt32() + ') from ' + mod(this.returnAddress));
    emit('  chain: ' + ftrace(this.context, 24));
  }
});

var nt = Process.findModuleByName('ntdll.dll');
Interceptor.attach(nt.findExportByName('RtlExitUserProcess'), {
  onEnter: function(a){
    emit('RtlExitUserProcess(' + a[0].toInt32() + ') from ' + mod(this.returnAddress));
    emit('  chain: ' + ftrace(this.context, 24));
  }
});
emit('diag29 ready');
