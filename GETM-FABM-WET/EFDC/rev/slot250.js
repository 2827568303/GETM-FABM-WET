'use strict';
function send2(s){ send(s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); if(m) return m.name+'+0x'+a.sub(m.base).toString(16);}catch(e){} return '?'; }
setTimeout(function(){
  try{
    var obj=ptr(0x16249b0).readPointer();
    send2('obj='+obj);
    if(obj.isNull()) return;
    var vt=obj.readPointer();
    send2('vtable='+vt+' ('+mod(vt)+')');
    var m=vt.add(0x250).readPointer();
    send2('slot250='+m+' ('+mod(m)+')');
    for(var off=0x240;off<=0x270;off+=4){
      var f=vt.add(off).readPointer();
      send2('  slot 0x'+off.toString(16)+' = '+f+' ('+mod(f)+')');
    }
  }catch(e){ send2('ERR '+e); }
}, 5200);
send2('loaded');
