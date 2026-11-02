'use strict';
function send2(s){ send(s); }
setTimeout(function(){
  var oa=Process.findModuleByName('oleaut32.dll');
  Interceptor.attach(oa.findExportByName('OleLoadPictureEx'),{
    onEnter:function(a){
      var out=[];
      for(var i=0;i<7;i++){
        var v=a[i];
        var d='';
        try{ d=' *=' + ptr(v).readU32().toString(16); }catch(e){ d=' *=(unreadable)'; }
        out.push('['+i+']='+v+d);
      }
      send2('OleLoadPictureEx args: '+out.join(' '));
    },
    onLeave:function(r){ send2('  hr=0x'+(r.toInt32()>>>0).toString(16)); }
  });
  send2('hooked');
}, 200);
send2('loaded');
