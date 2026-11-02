'use strict';
function send2(s){ send(s); }
setTimeout(function(){
  var oa=Process.findModuleByName('oleaut32.dll');
  Interceptor.attach(oa.findExportByName('OleLoadPictureEx'),{
    onEnter:function(a){
      send2('args8: [0]='+a[0]+' [1]='+a[1]+' [2]='+a[2]+' [3]='+a[3]+' [4]='+a[4]+' [5]='+a[5]+' [6]='+a[6]+' [7]='+a[7]);
      try{ send2('  *[7] = '+ptr(a[7]).readU32().toString(16)); }catch(e){ send2('  *[7] unreadable'); }
    }
  });
  send2('hooked');
}, 200);
send2('loaded');
