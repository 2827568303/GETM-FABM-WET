'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
var oa = Process.findModuleByName('oleaut32.dll');
['OleCreatePictureIndirect','OleLoadPicture','OleLoadPictureEx','OleLoadPicturePath','OleSavePictureFile'].forEach(function(n){
  var p = oa.findExportByName(n);
  if (!p) { emit('no '+n); return; }
  Interceptor.attach(p, { onEnter: function(a){ emit('CALL '+n); }, onLeave: function(r){ emit('  RET '+n+' hr=0x'+(r.toInt32()>>>0).toString(16)); } });
  emit('hooked '+n);
});
var u32 = Process.findModuleByName('user32.dll');
Interceptor.attach(u32.findExportByName('SoftModalMessageBox'),{onEnter:function(){ emit('=== MSGBOX ==='); }});
emit('ready');
