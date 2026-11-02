'use strict';
function send2(s){ send(s); }
setTimeout(function(){
  try{
    var oa=Process.findModuleByName('oleaut32.dll');
    var ole32=Process.findModuleByName('ole32.dll');
    var CreateStream=new NativeFunction(ole32.findExportByName('CreateStreamOnHGlobal'),'uint',['pointer','int','pointer']);
    // build 16x16 24bpp BMP
    var w=16,h=16,row=(w*3+3)&~3,size=54+row*h;
    var b=new Uint8Array(size); b[0]=0x42;b[1]=0x4D;
    var dv=new DataView(b.buffer); dv.setUint32(2,size,true); dv.setUint32(10,54,true);
    dv.setUint32(14,40,true); dv.setInt32(18,w,true); dv.setInt32(22,h,true);
    dv.setUint16(26,1,true); dv.setUint16(28,24,true); dv.setUint32(34,row*h,true);
    for(var i=54;i<size;i+=3){ b[i]=0x40;b[i+1]=0x80;b[i+2]=0xC0; }
    var mem=Memory.alloc(size); mem.writeByteArray(b);
    var pstm=Memory.alloc(4); CreateStream(ptr(0),1,pstm);
    var stm=pstm.readPointer(); var vt=stm.readPointer();
    var W=new NativeFunction(vt.add(16).readPointer(),'uint',['pointer','pointer','uint','pointer']);
    var S=new NativeFunction(vt.add(20).readPointer(),'uint',['pointer','int64','uint','pointer']);
    var n=Memory.alloc(4); W(stm,mem,size,n); S(stm,0,0,ptr(0));
    var cnt=0;
    Interceptor.attach(oa.findExportByName('OleLoadPictureEx'),{
      onEnter:function(a){
        cnt++;
        if(cnt===1){
          send2('replacing stream: old='+a[0]+' size='+a[1].toInt32());
          a[0]=stm; a[1]=ptr(size);
        }
      },
      onLeave:function(r){ send2('OleLoadPictureEx ret=0x'+((r.toInt32()>>>0).toString(16))+' (call #'+cnt+')'); }
    });
    send2('hooked, will substitute stream');
  }catch(e){ send2('ERR '+e); }
}, 300);
send2('loaded');
