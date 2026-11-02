'use strict';
function send2(s){ send(s); }
try { if (!Process.findModuleByName('ole32.dll')) Module.load('C:\\Windows\\SysWOW64\\ole32.dll'); } catch(e){ send2('load ole32 err '+e); }
try { if (!Process.findModuleByName('oleaut32.dll')) Module.load('C:\\Windows\\SysWOW64\\oleaut32.dll'); } catch(e){ send2('load oleaut32 err '+e); }
var B64 = "Qk02AwAAAAAAADYAAAAoAAAAEAAAABAAAAABABgAAAAAAAADAAATCwAAEwsAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA";
function decodeB64(s){
  var chars='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
  var out=[]; var buf=0, bits=0;
  for (var i=0;i<s.length;i++){ var c=s[i]; if(c==='=') break; var v=chars.indexOf(c); if(v<0) continue;
    buf=(buf<<6)|v; bits+=6; if(bits>=8){ bits-=8; out.push((buf>>bits)&0xff); } }
  return new Uint8Array(out);
}
setTimeout(function(){
  try {
    var ole32m = Process.findModuleByName('ole32.dll');
    var oleautm = Process.findModuleByName('oleaut32.dll');
    var CreateStreamOnHGlobal = new NativeFunction(ole32m.findExportByName('CreateStreamOnHGlobal'),'uint',['pointer','int','pointer']);
    var OleLoadPictureEx = new NativeFunction(oleautm.findExportByName('OleLoadPictureEx'),'uint',['pointer','int','int','pointer','int','int','int','pointer']);
    var ole32 = new NativeFunction(ole32m.findExportByName('OleInitialize'),'int',['pointer']);
    var hr0 = ole32(ptr(0));
    var data = decodeB64(B64);
    var mem = Memory.alloc(data.length); mem.writeByteArray(new Uint8Array(data));
    var pstm = Memory.alloc(4); CreateStreamOnHGlobal(ptr(0),1,pstm);
    var stm = pstm.readPointer(); var vt = stm.readPointer();
    var Write = new NativeFunction(vt.add(16).readPointer(),'uint',['pointer','pointer','uint','pointer']);
    var Seek = new NativeFunction(vt.add(20).readPointer(),'uint',['pointer','int64','uint','pointer']);
    var n = Memory.alloc(4); Write(stm, mem, data.length, n); Seek(stm,0,0,ptr(0));
    var iid = Memory.alloc(16);
    iid.writeByteArray(new Uint8Array([0x80,0x09,0xf8,0x7b,0x32,0xbf,0x1a,0x10,0x8b,0xbb,0x00,0xaa,0x00,0x30,0x0c,0xab]));
    var ppv = Memory.alloc(4);
    var hr = OleLoadPictureEx(stm, data.length, 0, iid, 0,0,0, ppv);
    send2('selftest oleInit=0x'+(hr0>>>0).toString(16)+' bmp len='+data.length+' hr=0x'+(hr>>>0).toString(16)+' pic='+ppv.readPointer());
  } catch(e){ send2('selftest err '+e); }
}, 800);
send2('loaded');
