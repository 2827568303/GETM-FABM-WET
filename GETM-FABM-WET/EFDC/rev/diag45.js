'use strict';
var vb = Process.findModuleByName('MSVBVM60.DLL');
function emit(s){ send(s); }
setTimeout(function(){
  try{
    var p = vb.findExportByName('rtcErrObj');
    emit('rtcErrObj @ ' + p);
    var f = new NativeFunction(p, 'pointer', []);
    var r = f();
    emit('returned ' + r);
    if (!r.isNull()) {
      var vt = r.readPointer();
      emit('vtable ' + vt);
    }
  }catch(e){ emit('err: ' + e); }
}, 2500);
emit('ready');
