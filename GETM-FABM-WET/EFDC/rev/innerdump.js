'use strict';
function send2(s){ send(s); }
function hexdump(p,n){ try{ var b=new Uint8Array(p.readByteArray(n)); var out=[]; for(var i=0;i<b.length;i++) out.push(('0'+b[i].toString(16)).slice(-2)); return out.join(' '); }catch(e){ return 'ERR '+e; } }
setTimeout(function(){
  try{
    var obj=ptr(0x16249b0).readPointer();
    if(obj.isNull()){ send2('null'); return; }
    var p1=obj.add(0x10).readPointer();
    var vt2=p1.readPointer();
    [0x1b8,0x250].forEach(function(off){
      var f=vt2.add(off).readPointer();
      send2('inner 0x'+off.toString(16)+' = '+f+' bytes: '+hexdump(f,24));
    });
  }catch(e){ send2('ERR '+e); }
}, 4200);
send2('loaded');
