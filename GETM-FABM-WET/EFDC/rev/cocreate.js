'use strict';
function send2(s){ send(s); }
setTimeout(function(){
  try{
    var ole32=Process.findModuleByName('ole32.dll')||Module.load('ole32.dll');
    var CoInit=new NativeFunction(ole32.findExportByName('CoInitializeEx'),'int',['pointer','uint']);
    var CoCreate=new NativeFunction(ole32.findExportByName('CoCreateInstance'),'uint',['pointer','pointer','uint','pointer','pointer']);
    CoInit(ptr(0),0);
    function guid(s){ var m=s.replace(/[{}]/g,'').split('-'); var b=new Uint8Array(16);
      var d1=parseInt(m[0],16), d2=parseInt(m[1],16), d3=parseInt(m[2],16);
      b[0]=d1&255;b[1]=(d1>>8)&255;b[2]=(d1>>16)&255;b[3]=(d1>>>24)&255;
      b[4]=d2&255;b[5]=(d2>>8)&255;b[6]=d3&255;b[7]=(d3>>8)&255;
      for(var i=0;i<8;i++) b[8+i]=parseInt(m[3].substr(i*2,2),16);
      for(var i=0;i<8;i++) b[8+i]=parseInt(m[4].substr(i*2,2),16);
      return b; }
    var clsid=guid('{2C247F23-8591-11D1-B16A-00C0F0283628}');
    var c=Memory.alloc(16); c.writeByteArray(clsid);
    var iid=guid('{00020400-0000-0000-C000-000000000046}');
    var i=Memory.alloc(16); i.writeByteArray(iid);
    var pp=Memory.alloc(4);
    var hr=CoCreate(c,ptr(0),1,i,pp);
    send2('CoCreateInstance(ImageList CLSID) hr=0x'+(hr>>>0).toString(16)+' obj='+pp.readPointer());
  }catch(e){ send2('ERR '+e); }
}, 600);
send2('loaded');
