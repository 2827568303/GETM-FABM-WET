'use strict';
function send2(s){ send(s); }
setTimeout(function(){
  try{
    var oa=Process.findModuleByName('oleaut32.dll');
    var OleInit=new NativeFunction(oa.findExportByName('OleInitialize'),'int',['pointer']);
    var hr=OleInit(ptr(0));
    send2('OleInitialize -> 0x'+(hr>>>0).toString(16));
    var olp=oa.findExportByName('OleLoadPictureEx');
    Interceptor.attach(olp,{ onLeave:function(r){ send2('OleLoadPictureEx hr=0x'+(r.toInt32()>>>0).toString(16)); } });
  }catch(e){ send2('ERR '+e); }
}, 1500);
send2('loaded');
