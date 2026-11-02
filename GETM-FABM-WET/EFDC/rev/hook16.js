'use strict';
function send2(s){ send(s); }
try { if(!Process.findModuleByName('ole32.dll')) Module.load('C:\\Windows\\SysWOW64\\ole32.dll'); } catch(e){}
try { if(!Process.findModuleByName('oleaut32.dll')) Module.load('C:\\Windows\\SysWOW64\\oleaut32.dll'); } catch(e){}
var B64="Qk02AwAAAAAAADYAAAAoAAAAEAAAABAAAAABABgAAAAAAAADAAATCwAAEwsAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA";
function dec(s){ var c='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'; var o=[],b=0,bit=0;
 for(var i=0;i<s.length;i++){var ch=s[i]; if(ch==='=')break; var v=c.indexOf(ch); if(v<0)continue; b=(b<<6)|v; bit+=6; if(bit>=8){bit-=8;o.push((b>>bit)&255);} } return new Uint8Array(o); }
var IID=null;
setTimeout(function(){
  try{
    var ole32=Process.findModuleByName('ole32.dll'), oleaut=Process.findModuleByName('oleaut32.dll');
    function N(m,n,r,a){ return new NativeFunction(m.findExportByName(n), r, a); }
    var CoInit=N(ole32,'CoInitializeEx','int',['pointer','int']);
    var OleInit=N(ole32,'OleInitialize','int',['pointer']);
    var CreateStream=N(ole32,'CreateStreamOnHGlobal','uint',['pointer','int','pointer']);
    var OleLoadPictureEx=N(oleaut,'OleLoadPictureEx','uint',['pointer','int','uint','pointer','uint','uint','uint','pointer']);
    var OleLoadPicture=N(oleaut,'OleLoadPicture','uint',['pointer','int','int','pointer','pointer']);
    var OleLoadPicturePath=N(oleaut,'OleLoadPicturePath','uint',['pointer','pointer','uint','uint','pointer']);
    var h1=OleInit(ptr(0));
    var data=dec(B64), mem=Memory.alloc(data.length); mem.writeByteArray(new Uint8Array(data));
    var iid=Memory.alloc(16); iid.writeByteArray(new Uint8Array([0x80,0x09,0xf8,0x7b,0x32,0xbf,0x1a,0x10,0x8b,0xbb,0x00,0xaa,0x00,0x30,0x0c,0xab]));
    function mkstm(){ var p=Memory.alloc(4); CreateStream(ptr(0),1,p); var stm=p.readPointer(); var vt=stm.readPointer();
      var W=new NativeFunction(vt.add(16).readPointer(),'uint',['pointer','pointer','uint','pointer']);
      var S=new NativeFunction(vt.add(20).readPointer(),'uint',['pointer','int64','uint','pointer']);
      var n=Memory.alloc(4); W(stm,mem,data.length,n); S(stm,0,0,ptr(0)); return stm; }
    var stm=mkstm(); var pp=Memory.alloc(4);
    var r1=OleLoadPictureEx(stm,data.length,0,iid,0,0,0,pp);
    var stm2=mkstm(); pp=Memory.alloc(4);
    var r2=OleLoadPicture(stm2,data.length,0,iid,pp);
    pp=Memory.alloc(4);
    var path=Memory.alloc(64); path.writeUtf16String('C:\\\\Users\\\\Public\\\\DSI\\\\EEMS8.3\\\\license.bmp');
    var r3=OleLoadPicturePath(path,ptr(0),0,0,pp);
    send2('oleInit=0x'+(h1>>>0).toString(16)+' Ex=0x'+(r1>>>0).toString(16)+' Plain=0x'+(r2>>>0).toString(16)+' Path=0x'+(r3>>>0).toString(16)+' pic='+pp.readPointer());
  }catch(e){ send2('err '+e); }
}, 900);
send2('loaded');
