'use strict';
function send2(s){ send(s); }
try { if(!Process.findModuleByName('ole32.dll')) Module.load('C:\\Windows\\SysWOW64\\ole32.dll'); } catch(e){}
try { if(!Process.findModuleByName('oleaut32.dll')) Module.load('C:\\Windows\\SysWOW64\\oleaut32.dll'); } catch(e){}
try { if(!Process.findModuleByName('gdi32.dll')) Module.load('C:\\Windows\\SysWOW64\\gdi32.dll'); } catch(e){}
function N(m,n,r,a){ return new NativeFunction(Process.findModuleByName(m).findExportByName(n), r, a); }
setTimeout(function(){
  try{
    var oleInit=N('ole32.dll','OleInitialize','int',['pointer'])(ptr(0));
    var CreateCompatibleDC=N('gdi32.dll','CreateCompatibleDC','pointer',['pointer'])(ptr(0));
    var CreateCompatibleBitmap=N('gdi32.dll','CreateCompatibleBitmap','pointer',['pointer','int','int'])(CreateCompatibleDC,16,16);
    var OleCreatePictureIndirect=N('oleaut32.dll','OleCreatePictureIndirect','uint',['pointer','pointer','int','pointer']);
    var desc=Memory.alloc(16);
    desc.writeU32(16); desc.add(4).writeU32(1); desc.add(8).writePointer(CreateCompatibleBitmap); desc.add(12).writePointer(ptr(0));
    var iid=Memory.alloc(16); iid.writeByteArray(new Uint8Array([0x80,0x09,0xf8,0x7b,0x32,0xbf,0x1a,0x10,0x8b,0xbb,0x00,0xaa,0x00,0x30,0x0c,0xab]));
    var ppv=Memory.alloc(4);
    var hr=OleCreatePictureIndirect(desc, iid, 0, ppv);
    send2('pictest oleInit=0x'+(oleInit>>>0).toString(16)+' hdc='+CreateCompatibleDC+' hbm='+CreateCompatibleBitmap+' OleCreatePictureIndirect hr=0x'+(hr>>>0).toString(16)+' pic='+ppv.readPointer());
  }catch(e){ send2('pictest err '+e); }
}, 900);
send2('loaded');
