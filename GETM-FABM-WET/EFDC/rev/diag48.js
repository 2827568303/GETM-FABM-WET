'use strict';
function emit(s){ send(s); }
var vb = Process.findModuleByName('MSVBVM60.DLL');
Interceptor.attach(vb.findExportByName('__vbaFileOpen'), { onEnter: function(a){
  var parts = [];
  for (var i=0;i<6;i++){
    var v = a[i];
    var s = '';
    try { s = v.readUtf16String(); } catch(e) { s = ''; }
    parts.push('a'+i+'='+v+(s ? ' ["'+s+'"]' : ''));
  }
  emit(parts.join('  '));
}});
emit('ready');
