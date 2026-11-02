'use strict';
function send2(s){ send(s); }
var T0=Date.now(); function t(){ return ((Date.now()-T0)/1000).toFixed(2); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); if(m) return m.name+'+0x'+a.sub(m.base).toString(16);}catch(e){} return String(a); }
setTimeout(function(){
  var u=Process.findModuleByName('user32.dll');
  Interceptor.attach(u.findExportByName('SetTimer'),{
    onEnter:function(a){ this.hwnd=a[0]; this.id=a[1].toInt32(); this.el=a[2].toInt32(); this.cb=a[3]; },
    onLeave:function(r){ send2('['+t()+'] SetTimer hwnd='+this.hwnd+' id='+this.id+' elapse='+this.el+' cb='+this.cb+' -> '+r); }
  });
  Interceptor.attach(u.findExportByName('KillTimer'),{
    onEnter:function(a){ send2('['+t()+'] KillTimer hwnd='+a[0]+' id='+a[1].toInt32()); }
  });
  Interceptor.attach(u.findExportByName('SetWindowPos'),{
    onEnter:function(a){ if((a[4].toInt32()&0x40)!==0) send2('['+t()+'] ShowWindow-ish '+a[0]); }
  });
  send2('hooked');
}, 250);
send2('loaded');
