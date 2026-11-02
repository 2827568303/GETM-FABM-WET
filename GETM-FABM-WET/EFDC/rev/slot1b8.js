'use strict';
function send2(s){ send(s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); if(m) return m.name+'+0x'+a.sub(m.base).toString(16);}catch(e){} return '?'; }
setTimeout(function(){
  try{
    var obj=ptr(0x16249b0).readPointer();
    send2('titleform='+obj);
    if(obj.isNull()) return;
    var vt=obj.readPointer();
    send2('vtable='+vt+' ('+mod(vt)+')');
    [0x1b8,0x250].forEach(function(off){
      var f=vt.add(off).readPointer();
      send2('slot 0x'+off.toString(16)+' = '+f+' ('+mod(f)+')');
    });
    var p1=obj.add(0x10).readPointer();
    var vt2=p1.readPointer();
    [0x1b8,0x250].forEach(function(off){
      var f=vt2.add(off).readPointer();
      send2('inner slot 0x'+off.toString(16)+' = '+f+' ('+mod(f)+')');
    });
  }catch(e){ send2('ERR '+e); }
}, 3400);
send2('loaded');
