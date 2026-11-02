'use strict';
function send2(s){ send(s); }
try { if (!Process.findModuleByName('ole32.dll')) Module.load('C:\\Windows\\SysWOW64\\ole32.dll'); } catch(e){}
try { if (!Process.findModuleByName('oleaut32.dll')) Module.load('C:\\Windows\\SysWOW64\\oleaut32.dll'); } catch(e){}
var B64 = "Qk02AwAAAAAAADYAAAAoAAAAEAAAABAAAAABABgAAAAAAAADAAATCwAAEwsAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA";
function decodeB64(s){ var chars='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'; var out=[]; var buf=0,bits=0;
  for(var i=0;i<s.length;i++){var c=s[i]; if(c==='=')break; var v=chars.indexOf(c); if(v<0)continue; buf=(buf<<6)|v; bits+=6; if(bits>=8){bits-=8; out.push((buf>>bits)&0xff);} } return new Uint8Array(out); }
var ole32m=Process.findModuleByName('ole32.dll'), oleautm=Process.findModuleByName('oleaut32.dll');
function N(m,n,r,a){ return new NativeFunction(m.findExportByName(n), r, a); }
var OleInitialize=N(ole32m,'OleInitialize','int',['pointer']);
var OleUninitialize=N(ole32m,'OleUninitialize','void',[]);
var CreateStreamOnHGlobal=N(ole32m,'CreateStreamOnHGlobal','uint',['pointer','int','pointer']);
var OleLoadPictureEx=N(oleautm,'OleLoadPictureEx','uint',['pointer','int','int','pointer','int','int','int','pointer']);
var data=decodeB64(B64), mem=Memory.alloc(data.length); mem.writeByteArray(new Uint8Array(data));
function load(){
  var pstm=Memory.alloc(4); CreateStreamOnHGlobal(ptr(0),1,pstm); var stm=pstm.readPointer(); var vt=stm.readPointer();
  var Write=N({findExportByName:function(){return ptr(0)},} ,'x','uint',[]);
  var W=new NativeFunction(vt.add(16).readPointer(),'uint',['pointer','pointer','uint','pointer']);
  var S=new NativeFunction(vt.add(20).readPointer(),'uint',['pointer','int64','uint','pointer']);
  var n=Memory.alloc(4); W(stm,mem,data.length,n); S(stm,0,0,ptr(0));
  var iid=Memory.alloc(16); iid.writeByteArray(new Uint8Array([0x80,0x09,0xf8,0x7b,0x32,0xbf,0x1a,0x10,0x8b,0xbb,0x00,0xaa,0x00,0x30,0x0c,0xab]));
  var ppv=Memory.alloc(4); var hr=OleLoadPictureEx(stm,data.length,0,iid,0,0,0,ppv);
  return 'hr=0x'+(hr>>>0).toString(16)+' pic='+ppv.readPointer();
}
setTimeout(function(){
  try{
    var a=OleInitialize(ptr(0)); var r1=load();
    OleUninitialize(); OleUninitialize(); OleUninitialize();
    var b=OleInitialize(ptr(0)); var r2=load();
    send2('oleInit1=0x'+(a>>>0).toString(16)+' first '+r1+' | after over-uninit oleInit2=0x'+(b>>>0).toString(16)+' second '+r2);
  }catch(e){ send2('err '+e); }
}, 800);
send2('loaded');
