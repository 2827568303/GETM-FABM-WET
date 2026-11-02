'use strict';
function send2(s){ send(s); }
function tryStr(p){
  try{ if(p.isNull()) return null; var s=p.readUtf16String(); if(s && s.length>1) return s; }catch(e){}
  try{ var q=p.readPointer(); if(!q.isNull()){ var s2=q.readUtf16String(); if(s2 && s2.length>1) return s2; } }catch(e){}
  try{ var a=p.readAnsiString(); if(a && a.length>1) return a; }catch(e){}
  return null;
}
var IID=[0x81,0x09,0xF8,0x7B,0x32,0xBF,0x1A,0x10,0x8B,0xBB,0x00,0xAA,0x00,0x30,0x0C,0xAB];
setTimeout(function(){
  try{
    var oa=Process.findModuleByName('oleaut32.dll');
    var gdi=Process.findModuleByName('gdi32.dll');
    var CreateBitmap=new NativeFunction(gdi.findExportByName('CreateBitmap'),'pointer',['int','int','uint','uint','pointer']);
    var OleCreate=new NativeFunction(oa.findExportByName('OleCreatePictureIndirect'),'uint',['pointer','pointer','int','pointer']);
    var iid=Memory.alloc(16); iid.writeByteArray(new Uint8Array(IID));
    Interceptor.attach(oa.findExportByName('OleLoadPictureEx'),{
      onEnter:function(a){ this.ppv=a[7]; },
      onLeave:function(r){
        if((r.toInt32()>>>0)===0) return;
        try{ var hbmp=CreateBitmap(2,2,1,1,ptr(0));
          var desc=Memory.alloc(16); desc.writeU32(16); desc.add(4).writeU32(1); desc.add(8).writePointer(hbmp); desc.add(12).writePointer(ptr(0));
          if((OleCreate(desc,iid,1,this.ppv)>>>0)===0) r.replace(ptr(0)); }catch(e){}
      }
    });
    var mb=Process.findModuleByName('MSVBVM60.DLL');
    var p=mb.findExportByName('__vbaFileOpen');
    Interceptor.attach(p,{
      onEnter:function(a){
        var s=null;
        for(var i=0;i<3 && !s;i++) s=tryStr(a[i]);
        send2('FileOpen '+(s?JSON.stringify(s):'(?)')+' args='+a[0]+','+a[1]+','+a[2]+','+a[3]);
      }
    });
    send2('ready');
  }catch(e){ send2('ERR '+e); }
}, 200);
send2('loaded');
