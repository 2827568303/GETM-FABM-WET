'use strict';
function send2(s){ send(s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); if(m) return m.name+'+0x'+a.sub(m.base).toString(16);}catch(e){} return '?'; }
var n=0;
var iv=setInterval(function(){
  n++;
  try{
    var obj=ptr(0x16249b0).readPointer();
    if(obj.isNull()){ if(n%5===0) send2('tick'+n+' null'); return; }
    var vt=obj.readPointer();
    send2('tick'+n+' obj='+obj+' vtable='+vt+' ('+mod(vt)+')');
    [0x1b8,0x250,0x94].forEach(function(off){
      var f=vt.add(off).readPointer();
      send2('  slot 0x'+off.toString(16)+' = '+f+' ('+mod(f)+')');
    });
    var p1=obj.add(0x10).readPointer();
    if(!p1.isNull()){
      var vt2=p1.readPointer();
      [0x1b8,0x250].forEach(function(off){
        var f=vt2.add(off).readPointer();
        send2('  inner 0x'+off.toString(16)+' = '+f+' ('+mod(f)+')');
      });
    }
    clearInterval(iv);
  }catch(e){ send2('ERR '+e); clearInterval(iv); }
}, 200);
setTimeout(function(){ clearInterval(iv); }, 9000);
send2('loaded');
