'use strict';
function send2(s){ send(s); }
setTimeout(function(){
  try{
    var ole32=Process.findModuleByName('ole32.dll'); var CoInit=new NativeFunction(ole32.findExportByName('CoInitializeEx'),'int',['pointer','uint']); var ci=CoInit(ptr(0),2); send2('CoInitializeEx='+ci); var h=Module.load('C:\\EFDC84_LIC\\mscomctl.ocx');
    var dgco=new NativeFunction(h.findExportByName('DllGetClassObject'),'uint',['pointer','pointer','pointer']);
    function guid(s){ var m=s.replace(/[{}]/g,'').split('-'); var b=new Uint8Array(16);
      var d1=parseInt(m[0],16), d2=parseInt(m[1],16), d3=parseInt(m[2],16);
      b[0]=d1&255;b[1]=(d1>>8)&255;b[2]=(d1>>16)&255;b[3]=(d1>>>24)&255;
      b[4]=d2&255;b[5]=(d2>>8)&255;b[6]=d3&255;b[7]=(d3>>8)&255;
      for(var i=0;i<8;i++) b[8+i]=parseInt(m[3].substr(i*2,2),16);
      for(var i=0;i<8;i++) b[8+i]=parseInt(m[4].substr(i*2,16)||m[4].substr(i*2,2),16);
      return b; }
    var c=Memory.alloc(16); c.writeByteArray(guid('{2C247F23-8591-11D1-B16A-00C0F0283628}'));
    var iid=Memory.alloc(16); iid.writeByteArray(guid('{00000001-0000-0000-C000-000000000046}'));
    var pp=Memory.alloc(4);
    var hr=dgco(c,iid,pp);
    send2('DllGetClassObject(ImageList) hr=0x'+(hr>>>0).toString(16)+' cf='+pp.readPointer());
    var c2=Memory.alloc(16); c2.writeByteArray(guid('{66833FE6-8583-11D1-B16A-00C0F0283628}'));
    var pp2=Memory.alloc(4); var hr2=dgco(c2,iid,pp2);
    send2('DllGetClassObject(Toolbar) hr=0x'+(hr2>>>0).toString(16)+' cf='+pp2.readPointer());
  }catch(e){ send2('ERR '+e); }
}, 600);
send2('loaded');
