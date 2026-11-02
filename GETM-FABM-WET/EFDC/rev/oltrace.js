'use strict';
function send2(s){ send(s); }
setTimeout(function(){
  try{
    var oa=Process.findModuleByName('oleaut32.dll');
    ['OleLoadPicture','OleLoadPictureEx','OleCreatePictureIndirect','OleSavePicture','OleLoadPicturePath'].forEach(function(fn){
      var p=oa.findExportByName(fn); if(!p) return;
      try{ Interceptor.attach(p,{ onEnter:function(){ send2('CALL '+fn); }, onLeave:function(r){ send2('  -> '+fn+' hr=0x'+(r.toInt32()>>>0).toString(16)); } }); }catch(e){}
    });
    var u=Process.findModuleByName('user32.dll');
    send2('hooked');
  }catch(e){ send2('ERR '+e); }
}, 200);
send2('loaded');
