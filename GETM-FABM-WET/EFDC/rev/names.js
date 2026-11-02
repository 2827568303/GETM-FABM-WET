'use strict';
function send2(s){ send(s); }
function gs(p){ var b=new Uint8Array(p.readByteArray(16)); function h(x){return ('0'+x.toString(16)).slice(-2);}
 var d1=(b[3]<<24|b[2]<<16|b[1]<<8|b[0])>>>0, d2=(b[5]<<8|b[4]), d3=(b[7]<<8|b[6]), s='';
 for(var i=8;i<16;i++) s+=h(b[i]);
 return ('00000000'+d1.toString(16)).slice(-8)+'-'+('0000'+d2.toString(16)).slice(-4)+'-'+('0000'+d3.toString(16)).slice(-4)+'-'+s.substr(0,4)+'-'+s.substr(4); }
function rstr(p){ try{ return p.isNull()?'':p.readUtf16String(); }catch(e){ return ''; } }
setTimeout(function(){
  try{
    var oa=Process.findModuleByName('oleaut32.dll')||Module.load('oleaut32.dll');
    var LoadTypeLib=new NativeFunction(oa.findExportByName('LoadTypeLib'),'uint',['pointer','pointer']);
    var f='C:\\EFDC84_LIC\\mscomctl.ocx';
    var p=Memory.alloc(520); p.writeUtf16String(f); var out=Memory.alloc(4);
    var hr=LoadTypeLib(p,out); if(hr!==0){ send2('load hr=0x'+(hr>>>0).toString(16)); return; }
    var tl=out.readPointer(); var vt=tl.readPointer();
    var GetCount=new NativeFunction(vt.add(12).readPointer(),'uint',['pointer']);
    var GetTI=new NativeFunction(vt.add(16).readPointer(),'uint',['pointer','uint','pointer']);
    var GetTIT=new NativeFunction(vt.add(20).readPointer(),'uint',['pointer','uint','pointer']);
    var n=GetCount(tl);
    for(var i=0;i<n;i++){
      var kind=Memory.alloc(4); if(GetTIT(tl,i,kind)!==0) continue;
      if(kind.readU32()!==5) continue;
      var ti=Memory.alloc(4); if(GetTI(tl,i,ti)!==0) continue;
      var info=ti.readPointer(); var ivt=info.readPointer();
      var GetTypeAttr=new NativeFunction(ivt.add(12).readPointer(),'uint',['pointer','pointer']);
      var GetDoc=new NativeFunction(ivt.add(48).readPointer(),'uint',['pointer','int','pointer','pointer','pointer','pointer']);
      var RelTA=new NativeFunction(ivt.add(76).readPointer(),'void',['pointer','pointer']);
      var ta=Memory.alloc(4);
      if(GetTypeAttr(info,ta)!==0) continue;
      var attr=ta.readPointer();
      var nm=Memory.alloc(4), d=Memory.alloc(4), hf=Memory.alloc(4), cx=Memory.alloc(4);
      var name='';
      if(GetDoc(info,-1,nm,d,hf,cx)===0) name=rstr(nm.readPointer());
      send2('COCLASS '+gs(attr)+'  '+name);
      RelTA(info,attr);
    }
  }catch(e){ send2('ERR '+e); }
}, 600);
send2('loaded');
