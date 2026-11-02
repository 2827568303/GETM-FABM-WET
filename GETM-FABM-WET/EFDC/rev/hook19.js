'use strict';
function send2(s){ send(s); }
setTimeout(function(){
  try{
    var k32=Process.findModuleByName('kernel32.dll');
    var LLW=new NativeFunction(k32.findExportByName('LoadLibraryW'),'pointer',['pointer']);
    var LLN=new NativeFunction(k32.findExportByName('LoadLibraryA'),'pointer',['pointer']);
    var GE=new NativeFunction(k32.findExportByName('GetLastError'),'uint',[]);
    var nm=Memory.alloc(64); nm.writeUtf16String('gdiplus.dll');
    var h=LLW(nm); var e1=GE();
    var na=Memory.alloc(32); na.writeAnsiString('gdiplus.dll');
    var h2=LLN(na); var e2=GE();
    var out='LoadLibraryW(gdiplus)='+h+' err='+e1+' LoadLibraryA='+h2+' err='+e2;
    if(!h.isNull()){
      var gm=Process.findModuleByName('gdiplus.dll');
      if(gm){
        var GS=new NativeFunction(gm.findExportByName('GdiplusStartup'),'uint',['pointer','pointer','pointer']);
        var tok=Memory.alloc(4); var inp=Memory.alloc(16);
        inp.writeU32(1); inp.add(4).writeU32(0); inp.add(8).writePointer(ptr(0)); inp.add(12).writeU32(0);
        var hr=GS(tok,inp,ptr(0));
        out+=' GdiplusStartup=0x'+(hr>>>0).toString(16)+' tok='+tok.readU32();
      } else out+=' gdiplus not in module list';
    }
    send2(out);
  }catch(e){ send2('err '+e); }
}, 900);
send2('loaded');
