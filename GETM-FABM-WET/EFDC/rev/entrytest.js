'use strict';
function send2(s){ send(s); }
var done=false;
function test(tag){
  try{
    var oa=Process.findModuleByName('oleaut32.dll'), ole32=Process.findModuleByName('ole32.dll');
    if(!oa||!ole32){ send2(tag+' modules missing'); return; }
    var CoInit=new NativeFunction(ole32.findExportByName('CoInitializeEx'),'int',['pointer','uint']);
    CoInit(ptr(0),2);
    var CreateStream=new NativeFunction(ole32.findExportByName('CreateStreamOnHGlobal'),'uint',['pointer','int','pointer']);
    var OleLoad=new NativeFunction(oa.findExportByName('OleLoadPictureEx'),'uint',['pointer','int','uint','pointer','uint','uint','uint','pointer']);
    var w=16,h=16,row=(w*3+3)&~3,size=54+row*h;
    var b=new Uint8Array(size); b[0]=0x42;b[1]=0x4D;
    var dv=new DataView(b.buffer); dv.setUint32(2,size,true); dv.setUint32(10,54,true);
    dv.setUint32(14,40,true); dv.setInt32(18,w,true); dv.setInt32(22,h,true);
    dv.setUint16(26,1,true); dv.setUint16(28,24,true); dv.setUint32(34,row*h,true);
    var mem=Memory.alloc(size); mem.writeByteArray(b);
    var p=Memory.alloc(4); CreateStream(ptr(0),1,p); var stm=p.readPointer(); var vt=stm.readPointer();
    var W=new NativeFunction(vt.add(16).readPointer(),'uint',['pointer','pointer','uint','pointer']);
    var S=new NativeFunction(vt.add(20).readPointer(),'uint',['pointer','int64','uint','pointer']);
    var n=Memory.alloc(4); W(stm,mem,size,n); S(stm,0,0,ptr(0));
    var iid=Memory.alloc(16); iid.writeByteArray(new Uint8Array([0x80,0x09,0xf8,0x7b,0x32,0xbf,0x1a,0x10,0x8b,0xbb,0x00,0xaa,0x00,0x30,0x0c,0xab]));
    var pp=Memory.alloc(4);
    var hr=OleLoad(stm,size,0,iid,0,0,0,pp);
    send2(tag+' OleLoadPictureEx hr=0x'+(hr>>>0).toString(16)+' pic='+pp.readPointer());
  }catch(e){ send2(tag+' ERR '+e); }
}
setTimeout(function(){
  try{
    Interceptor.attach(ptr(0x451954), { onEnter: function(){ if(!done){ done=true; setTimeout(function(){ test('at-entry'); }, 30); } } });
    send2('hooked entry');
  }catch(e){ send2('ERR '+e); }
}, 50);
send2('loaded');
