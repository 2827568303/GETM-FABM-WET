'use strict';
function send2(s){ send(s); }
setTimeout(function(){
  try{
    var oa=Process.findModuleByName('oleaut32.dll')||Module.load('oleaut32.dll');
    var LoadTypeLib=new NativeFunction(oa.findExportByName('LoadTypeLib'),'uint',['pointer','pointer']);
    var f='C:\\Users\\23801\\Desktop\\GETM-FABM-WET-260928\\GETM-FABM-WET\\EFDC\\EFDC 商业版8.4\\mscomctl.ocx';
    var p=Memory.alloc(520); p.writeUtf16String(f); var out=Memory.alloc(4);
    var hr=LoadTypeLib(p,out); var tl=out.readPointer();
    send2('hr=0x'+(hr>>>0).toString(16)+' tl='+tl);
    var raw=tl.readByteArray(16); send2('tl bytes '+Array.from(new Uint8Array(raw)).map(function(b){return ('0'+b.toString(16)).slice(-2);}).join(''));
    var vt=tl.readPointer(); send2('vt='+vt);
    var vtbytes=vt.readByteArray(48); send2('vt dwords '+Array.from(new Uint32Array(vtbytes)).map(function(x){return x.toString(16);}).join(','));
  }catch(e){ send2('ERR '+e); }
}, 600);
send2('loaded');
