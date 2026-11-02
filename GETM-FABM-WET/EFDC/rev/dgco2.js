'use strict';
function send2(s){ send(s); }
setTimeout(function(){
  try{
    var adv=Process.findModuleByName('advapi32.dll')||Module.load('advapi32.dll');
    var RegOpen=new NativeFunction(adv.findExportByName('RegOpenKeyExW'),'uint',['pointer','pointer','uint','uint','pointer']);
    var RegOvr=new NativeFunction(adv.findExportByName('RegOverridePredefKey'),'uint',['pointer','pointer']);
    var sub=Memory.alloc(128); sub.writeUtf16String('Software\\Classes'); var ph=Memory.alloc(4);
    RegOpen(ptr(0x80000001), sub, 0, 0x000F003F, ph);
    var hr0=RegOvr(ptr(0x80000000), ph.readPointer());
    var h=Module.load('C:\\EFDC84_LIC\\mscomctl.ocx');
    var dgco=new NativeFunction(h.findExportByName('DllGetClassObject'),'uint',['pointer','pointer','pointer']);
    function guid(s){ var m=s.replace(/[{}]/g,'').split('-'); var b=new Uint8Array(16);
      var d1=parseInt(m[0],16), d2=parseInt(m[1],16), d3=parseInt(m[2],16);
      b[0]=d1&255;b[1]=(d1>>8)&255;b[2]=(d1>>16)&255;b[3]=(d1>>>24)&255;
      b[4]=d2&255;b[5]=(d2>>8)&255;b[6]=d3&255;b[7]=(d3>>8)&255;
      for(var i=0;i<8;i++) b[8+i]=parseInt(m[3].substr(i*2,2),16);
      for(var i=0;i<8;i++) b[8+i]=parseInt(m[4].substr(i*2,2),16);
      return b; }
    var c=Memory.alloc(16); c.writeByteArray(guid('{2C247F23-8591-11D1-B16A-00C0F0283628}'));
    var iid=Memory.alloc(16); iid.writeByteArray(guid('{00000001-0000-0000-C000-000000000046}'));
    var pp=Memory.alloc(4);
    var hr=dgco(c,iid,pp);
    send2('override=' + hr0 + ' DllGetClassObject hr=0x'+(hr>>>0).toString(16)+' cf='+pp.readPointer());
  }catch(e){ send2('ERR '+e); }
}, 600);
send2('loaded');
