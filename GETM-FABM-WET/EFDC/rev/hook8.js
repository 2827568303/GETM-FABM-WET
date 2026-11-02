'use strict';
var T0 = Date.now();
function t(){ return ((Date.now()-T0)/1000).toFixed(2); }
function send2(s){ send(s); }
var B64 = "Qk02AwAAAAAAADYAAAAoAAAAEAAAABAAAAABABgAAAAAAAADAAATCwAAEwsAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA";
var bmpBytes = null;
function decodeB64(s){
  var chars='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
  var out=[]; var buf=0, bits=0;
  for (var i=0;i<s.length;i++){
    var c=s[i]; if(c==='=') break; var v=chars.indexOf(c); if(v<0) continue;
    buf=(buf<<6)|v; bits+=6; if(bits>=8){ bits-=8; out.push((buf>>bits)&0xff); }
  }
  return new Uint8Array(out);
}
var ole32m = Process.findModuleByName('ole32.dll');
var oleautm = Process.findModuleByName('oleaut32.dll');
var CreateStreamOnHGlobal = new NativeFunction(ole32m.findExportByName('CreateStreamOnHGlobal'),'uint',['pointer','int','pointer']);
var OleLoadPictureEx = new NativeFunction(oleautm.findExportByName('OleLoadPictureEx'),'uint',['pointer','int','int','pointer','int','int','int','pointer']);
function selfTest(){
  try{
    var data = decodeB64(B64);
    var mem = Memory.alloc(data.length); mem.writeByteArray(data.buffer? new Uint8Array(data): data);
    var pstm = Memory.alloc(4);
    CreateStreamOnHGlobal(ptr(0),1,pstm);
    var stm = pstm.readPointer();
    var vt = stm.readPointer();
    var Write = new NativeFunction(vt.add(16).readPointer(),'uint',['pointer','pointer','uint','pointer']);
    var Seek = new NativeFunction(vt.add(20).readPointer(),'uint',['pointer','int64','uint','pointer']);
    var n = Memory.alloc(4);
    Write(stm, mem, data.length, n);
    Seek(stm,0,0,ptr(0));
    var iid = Memory.alloc(16);
    iid.writeByteArray(new Uint8Array([0x80,0x09,0xf8,0x7b,0x32,0xbf,0x1a,0x10,0x8b,0xbb,0x00,0xaa,0x00,0x30,0x0c,0xab]));
    var ppv = Memory.alloc(4);
    var hr = OleLoadPictureEx(stm, data.length, 0, iid, 0,0,0, ppv);
    send2('['+t()+'] selftest bmp len='+data.length+' hr=0x'+(hr>>>0).toString(16)+' pic='+ppv.readPointer());
  }catch(e){ send2('['+t()+'] selftest err '+e); }
}
[500,1500,2500,3500,4500,5500,6500,8000,10000,12000].forEach(function(ms){ setTimeout(selfTest, ms); });
send2('script loaded');
