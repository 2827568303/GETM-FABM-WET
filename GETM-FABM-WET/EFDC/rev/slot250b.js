'use strict';
function send2(s){ send(s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); if(m) return m.name+'+0x'+a.sub(m.base).toString(16);}catch(e){} return '?'; }
var n=0;
var iv=setInterval(function(){
  n++;
  try{
    var obj=ptr(0x16249b0).readPointer();
    if(obj.isNull()){ if(n%4===0) send2('tick'+n+' obj=null'); return; }
    var vt=obj.readPointer();
    send2('tick'+n+' obj='+obj+' vtable='+vt+' ('+mod(vt)+')');
    var m=vt.add(0x250).readPointer();
    send2('  slot250='+m+' ('+mod(m)+')');
    clearInterval(iv);
  }catch(e){ send2('ERR '+e); clearInterval(iv); }
}, 500);
setTimeout(function(){ clearInterval(iv); }, 11000);
send2('loaded');
