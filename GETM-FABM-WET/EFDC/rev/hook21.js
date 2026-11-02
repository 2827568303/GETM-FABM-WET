'use strict';
function send2(s){ send(s); }
setTimeout(function(){
  try{
    var g32=Process.findModuleByName('gdi32.dll'), o32=Process.findModuleByName('ole32.dll'), oa=Process.findModuleByName('oleaut32.dll');
    function N(m,n,r,a){ return new NativeFunction(m.findExportByName(n), r, a); }
    N(o32,'OleInitialize','int',['pointer'])(ptr(0));
    var CreateDIBSection=N(g32,'CreateDIBSection','pointer',['pointer','pointer','uint','pointer','pointer','uint']);
    var bmi=Memory.alloc(64);
    bmi.writeU32(40); bmi.add(4).writeS32(16); bmi.add(8).writeS32(16);
    bmi.add(12).writeU16(1); bmi.add(14).writeU16(24); bmi.add(16).writeU32(0);
    bmi.add(20).writeU32(16*16*3);
    var bits=Memory.alloc(4);
    var hbmp=CreateDIBSection(ptr(0), bmi, 0, bits, ptr(0), 0);
    var OleCPI=N(oa,'OleCreatePictureIndirect','uint',['pointer','pointer','int','pointer']);
    var desc=Memory.alloc(16);
    desc.writeU32(16); desc.add(4).writeU32(1); desc.add(8).writePointer(hbmp); desc.add(12).writePointer(ptr(0));
    var iid=Memory.alloc(16); iid.writeByteArray(new Uint8Array([0x80,0x09,0xf8,0x7b,0x32,0xbf,0x1a,0x10,0x8b,0xbb,0x00,0xaa,0x00,0x30,0x0c,0xab]));
    var pp=Memory.alloc(4);
    var hr=OleCPI(desc, iid, 0, pp);
    send2('DIBSection='+hbmp+' bits='+bits.readPointer()+' OleCreatePictureIndirect(DIB) hr=0x'+(hr>>>0).toString(16)+' pic='+pp.readPointer());
  }catch(e){ send2('err '+e); }
}, 900);
send2('loaded');
