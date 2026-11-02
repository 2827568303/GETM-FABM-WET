'use strict';
function send2(s){ send(s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); if(m) return m.name+'+0x'+a.sub(m.base).toString(16);}catch(e){} return '?'; }
setTimeout(function(){
  try{
    var obj=ptr(0x16249b0).readPointer();
    send2('obj='+obj+' ('+mod(obj)+')');
    if(obj.isNull()) return;
    var p1=obj.add(0x10).readPointer();
    send2('obj+0x10='+p1+' ('+mod(p1)+')');
    var vt=p1.readPointer();
    send2('[obj+0x10]='+vt+' ('+mod(vt)+')');
    var impl=vt.add(0x250).readPointer();
    send2('impl vtable[0x250]='+impl+' ('+mod(impl)+')');
    for(var off=0x240;off<=0x260;off+=4){
      var f=vt.add(off).readPointer();
      send2('  slot 0x'+off.toString(16)+' = '+f+' ('+mod(f)+')');
    }
  }catch(e){ send2('ERR '+e); }
}, 4500);
send2('loaded');

