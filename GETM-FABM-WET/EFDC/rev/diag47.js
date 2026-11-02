'use strict';
function emit(s){ send(s); }
var vb = Process.findModuleByName('MSVBVM60.DLL');
var pOpen = vb.findExportByName('__vbaFileOpen');
emit('__vbaFileOpen @ ' + pOpen);
Interceptor.attach(pOpen, { onEnter: function(a){
  var out = [];
  for (var i=0;i<4;i++){ try{ out.push(a[i].toString()); }catch(e){ out.push('?'); } }
  var s = '';
  try{ s = a[1].readUtf16String(); }catch(e){ try{ s = a[2].readUtf16String(); }catch(e2){} }
  emit('FileOpen args=' + out.join(',') + '   path=' + JSON.stringify(s));
}});
emit('ready');
