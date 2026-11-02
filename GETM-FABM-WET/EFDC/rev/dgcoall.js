'use strict';
function send2(s){ send(s); }
setTimeout(function(){
  try{
    var h=Module.load('C:\\EFDC84_LIC\\mscomctl.ocx');
    var dgco=new NativeFunction(h.findExportByName('DllGetClassObject'),'uint',['pointer','pointer','pointer']);
    function guid(s){ var m=s.replace(/[{}]/g,'').split('-'); var b=new Uint8Array(16);
      var d1=parseInt(m[0],16), d2=parseInt(m[1],16), d3=parseInt(m[2],16);
      b[0]=d1&255;b[1]=(d1>>8)&255;b[2]=(d1>>16)&255;b[3]=(d1>>>24)&255;
      b[4]=d2&255;b[5]=(d2>>8)&255;b[6]=d3&255;b[7]=(d3>>8)&255;
      for(var i=0;i<4;i++) b[8+i]=parseInt(m[3].substr(i*2,2),16);
      for(var i=0;i<8;i++) b[12+i]=parseInt(m[4].substr(i*2,2),16);
      return b; }
    var iid=Memory.alloc(16); iid.writeByteArray(guid('{00000001-0000-0000-C000-000000000046}'));
    var list='2334d2b2-713e-11cf-8ae5-00aa00c00905 2334d2b4-713e-11cf-8ae5-00aa00c00905 1efb6596-857c-11d1-b16a-00c0f0283628 1efb6598-857c-11d1-b16a-00c0f0283628 1efb659a-857c-11d1-b16a-00c0f0283628 66833fe6-8583-11d1-b16a-00c0f0283628 66833fe8-8583-11d1-b16a-00c0f0283628 66833fea-8583-11d1-b16a-00c0f0283628 66833fec-8583-11d1-b16a-00c0f0283628 66833fee-8583-11d1-b16a-00c0f0283628 8e3867a3-8586-11d1-b16a-00c0f0283628 8e3867a5-8586-11d1-b16a-00c0f0283628 8e3867ab-8586-11d1-b16a-00c0f0283628 35053a22-8589-11d1-b16a-00c0f0283628 c74190b6-8589-11d1-b16a-00c0f0283628 bdd1f04b-858b-11d1-b16a-00c0f0283628 2c247f23-8591-11d1-b16a-00c0f0283628 2c247f25-8591-11d1-b16a-00c0f0283628 2c247f27-8591-11d1-b16a-00c0f0283628 f08df954-8592-11d1-b16a-00c0f0283628 c8a3dc01-8593-11d1-b16a-00c0f0283628 dd9da666-8594-11d1-b16a-00c0f0283628'.split(' ');
    var okcc=0;
    list.forEach(function(s){
      var c=Memory.alloc(16); c.writeByteArray(guid('{'+s+'}')); var pp=Memory.alloc(4);
      var hr=dgco(c,iid,pp);
      if(hr===0){ okcc++; send2('OK '+s); }
    });
    send2('total ok='+okcc+' of '+list.length);
  }catch(e){ send2('ERR '+e); }
}, 600);
send2('loaded');
