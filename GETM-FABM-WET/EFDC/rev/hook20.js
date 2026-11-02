'use strict';
function send2(s){ send(s); }
setTimeout(function(){
  try{
    var m=Process.findModuleByName('oleaut32.dll');
    var p=m.findExportByName('OleLoadPictureEx');
    var q=m.findExportByName('OleLoadPicture');
    send2('oleaut32@'+m.base+' ex='+p+' bytes='+p.readByteArray(12).toString? '' : '');
    send2('EXBYTES '+Array.from(new Uint8Array(p.readByteArray(12))).map(function(b){return ('0'+b.toString(16)).slice(-2);}).join(''));
    send2('PLAINBYTES '+Array.from(new Uint8Array(q.readByteArray(12))).map(function(b){return ('0'+b.toString(16)).slice(-2);}).join(''));
  }catch(e){ send2('err '+e); }
}, 900);
send2('loaded');
