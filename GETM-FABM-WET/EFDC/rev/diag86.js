'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
var k32=Process.findModuleByName('kernel32.dll');
var Sleep=new NativeFunction(k32.findExportByName('Sleep'),'void',['uint']);
var pExit=k32.findExportByName('ExitProcess');
Interceptor.replace(pExit, new NativeCallback(function(code){
  emit('ExitProcess('+code+') blocked; sleeping forever on tid='+Process.getCurrentThreadId());
  Sleep(0xFFFFFFFF);
}, 'void', ['uint']));
emit('ready (ExitProcess blocked)');
