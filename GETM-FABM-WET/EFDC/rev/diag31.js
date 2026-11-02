'use strict';
// diag31.js — 让 VB 的 End 变成空操作，看程序是否继续走
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }

var vb = Process.findModuleByName('MSVBVM60.DLL');
var pEnd = vb.findExportByName('__vbaEnd');
emit('__vbaEnd @ ' + pEnd);
try {
  Interceptor.replace(pEnd, new NativeCallback(function(){
    emit('  __vbaEnd 被拦截（不退出）');
  }, 'void', []));
  emit('__vbaEnd replaced');
} catch (e) { emit('replace fail ' + e); }

// 顺便广告框：直接返回 IDOK
try{
  var u32 = Process.findModuleByName('user32.dll');
  var pSoft = u32.findExportByName('SoftModalMessageBox');
  Interceptor.replace(pSoft, new NativeCallback(function(pms){
    try{ var t = pms.add(0xC).readPointer(); emit('  msgbox swallowed: ' + JSON.stringify(t.isNull()?'':t.readUtf16String())); }catch(e){}
    return 1;
  }, 'int', ['pointer']));
  emit('SoftModalMessageBox swallowed');
}catch(e){ emit('soft replace fail ' + e); }

emit('diag31 ready');
