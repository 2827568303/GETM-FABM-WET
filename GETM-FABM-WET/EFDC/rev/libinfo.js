'use strict';
function send2(s){ send(s); }
function gs(p){ var b=new Uint8Array(p.readByteArray(16)); function h(x){return ('0'+x.toString(16)).slice(-2);}
 var d1=(b[3]<<24|b[2]<<16|b[1]<<8|b[0])>>>0, d2=(b[5]<<8|b[4]), d3=(b[7]<<8|b[6]), s='';
 for(var i=8;i<16;i++) s+=h(b[i]);
 return ('00000000'+d1.toString(16)).slice(-8)+'-'+('0000'+d2.toString(16)).slice(-4)+'-'+('0000'+d3.toString(16)).slice(-4)+'-'+s.substr(0,4)+'-'+s.substr(4); }
setTimeout(function(){
  try{
    var oa=Process.findModuleByName('oleaut32.dll')||Module.load('oleaut32.dll');
    var LoadTypeLib=new NativeFunction(oa.findExportByName('LoadTypeLib'),'uint',['pointer','pointer']);
    ['mscomctl.ocx','comctl32.ocx'].forEach(function(fn){
      var f='C:\\Users\\23801\\Desktop\\GETM-FABM-WET-260928\\GETM-FABM-WET\\EFDC\\EFDC 商业版8.4\\'+fn;
      var p=Memory.alloc(520); p.writeUtf16String(f); var out=Memory.alloc(4);
      var hr=LoadTypeLib(p,out); if(hr!==0){ send2(fn+' hr=0x'+(hr>>>0).toString(16)); return; }
      var tl=out.readPointer(); var vt=tl.readPointer();
      var GetLibAttr=new NativeFunction(vt.add(28).readPointer(),'uint',['pointer','pointer']);
      var la=Memory.alloc(4);
      if(GetLibAttr(tl,la)!==0){ send2(fn+' libattr fail'); return; }
      var a=la.readPointer(); var b=new Uint8Array(a.readByteArray(32));
      send2('LIB '+fn+' '+gs(a)+' v'+(b[24]|(b[25]<<8))+'.'+(b[26]|(b[27]<<8)));
    });
  }catch(e){ send2('ERR '+e); }
}, 600);
send2('loaded');
