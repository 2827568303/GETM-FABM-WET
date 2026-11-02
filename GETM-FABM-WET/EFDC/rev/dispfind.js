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
  }catch(e){}
}, 200);
var n=0;
var iv=setInterval(function(){
  n++;
  try{
    var obj=ptr(0x16249b0).readPointer();
    if(obj.isNull()) return;
    var p1=obj.add(0x10).readPointer();
    if(p1.isNull()) return;
    var vt2=p1.readPointer();
    var thunk=vt2.add(0x250).readPointer();
    var b=new Uint8Array(thunk.readByteArray(24));
    // find B9 (mov ecx,imm32) at offset 13
    var disp=null;
    for(var i=0;i<b.length-5;i++){ if(b[i]===0xB9){ disp=(b[i+1]|(b[i+2]<<8)|(b[i+3]<<16)|(b[i+4]<<24))>>>0; break; } }
    var mb=Process.findModuleByName('MSVBVM60.DLL');
    var rva=disp?((disp-mb.base.toUInt32())>>>0):null;
    emit('obj='+obj+' thunk='+thunk+' dispatcher='+(disp?('0x'+disp.toString(16)):'?')+' rva='+(rva!==null?('0x'+rva.toString(16)):'?')+' base='+mb.base);
    clearInterval(iv);
  }catch(e){ emit('ERR '+e); clearInterval(iv); }
}, 500);
setTimeout(function(){ clearInterval(iv); }, 12000);
emit('loaded');
