'use strict';
function send2(s){ send(s); }
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
    Interceptor.attach(mb.findExportByName('__vbaFileOpen'),{
      onEnter:function(a){
        try{
          var p=a[3];
          if(p.isNull()) return;
          var s=p.readUtf16String();
          if(s && s.indexOf('ee_activation.log')>=0){
            // overwrite in place: "log" -> "txt" (same length)
            var n=s.length;
            var np=p.add((n-3)*2);
            np.writeUtf16String('txt');
            send2('redirected log -> tct');
          }
        }catch(e){}
      }
    });
    send2('ready');
  }catch(e){ send2('ERR '+e); }
}, 200);
send2('loaded');
