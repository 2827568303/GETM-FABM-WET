'use strict';
// diag22.js — 记录 481 弹框的调用点（用于定位错误处理代码）
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }
function bt(ctx){ try{ return Thread.backtrace(ctx, Backtracer.FUZZY).slice(0,14).map(mod).join(' <- '); }catch(e){ return '?'; } }

var u32 = Process.findModuleByName('user32.dll');
var p = u32.findExportByName('SoftModalMessageBox');
Interceptor.attach(p, { onEnter: function(a){
  try{
    var pms = a[0];
    var t = pms.add(0xC).readPointer();
    emit('SoftModal caller=' + mod(this.returnAddress) + ' text=' + JSON.stringify(t.isNull()?'':t.readUtf16String()));
    emit('  chain: ' + bt(this.context));
  }catch(e){ emit('err ' + e); }
}});

// VB6 错误抛出器
var vb = Process.findModuleByName('MSVBVM60.DLL');
try{
  var raiser = vb.base.add(0x384a7);
  Interceptor.attach(raiser, { onEnter: function(){
    emit('VB RAISE err=' + this.context.esp.add(4).readU32() + ' ret=' + mod(this.returnAddress));
    emit('  chain: ' + bt(this.context));
  }});
  emit('raiser hooked ' + raiser);
}catch(e){ emit('raiser hook fail ' + e); }

// 屏蔽弹框：直接返回 IDOK(1)，让流程继续（不显示窗口）
try{
  Interceptor.replace(p, new NativeCallback(function(pms){ emit('  [swallowed] SoftModalMessageBox'); return 1; }, 'int', ['pointer']));
  emit('SoftModalMessageBox replaced (自动按 OK)');
}catch(e){ emit('replace fail ' + e); }

emit('diag22 ready');
