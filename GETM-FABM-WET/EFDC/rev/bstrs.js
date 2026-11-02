'use strict';
function send2(s){ send(s); }
function bstr(p){ try{ if(p.isNull()) return null; var len=p.sub(4).readU32(); return p.readUtf16String(len/2); }catch(e){ return '<err>'; } }
setTimeout(function(){
  [0x4E5338,0x4E92DC,0x4E5390,0x4E9334,0x4E93E0,0x4E9384,0x4E545C,0x4F96D0,0x4F9760].forEach(function(va){
    try{
      var p=ptr(va).readPointer();
      send2('global 0x'+va.toString(16)+' -> '+p+' = '+JSON.stringify(bstr(p)));
    }catch(e){ send2('global 0x'+va.toString(16)+' ERR '+e); }
  });
}, 3500);
send2('loaded');
