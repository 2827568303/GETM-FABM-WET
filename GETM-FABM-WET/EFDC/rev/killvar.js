'use strict';
function emit(s){ send(s); }
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
    Interceptor.attach(ptr(0x81D991),{
      onEnter:function(){
        try{
          var ebp=this.context.ebp;
          var vt=ebp.sub(0x70).readU32();
          var pstr=ebp.sub(0x68).readPointer();
          var s='';
          try{ s=pstr.readUtf16String(); }catch(e){ s='<unreadable>'; }
          emit('Kill-VARIANT vt=0x'+vt.toString(16)+' ptr='+pstr+' str='+JSON.stringify(s));
          var lic=ptr(0x162040C).readPointer();
          var ls='';
          try{ ls=lic.readUtf16String(); }catch(e){ ls='<unreadable>'; }
          emit('   [0x162040C]='+lic+' = '+JSON.stringify(ls));
        }catch(e){ emit('read err '+e); }
      }
    });
    emit('ready');
  }catch(e){ emit('ERR '+e); }
}, 200);
emit('loaded');
