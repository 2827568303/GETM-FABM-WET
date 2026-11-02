'use strict';
function send2(s){ send(s); }
var T0=Date.now(); function t(){ return ((Date.now()-T0)/1000).toFixed(2); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); if(m) return m.name+'+0x'+a.sub(m.base).toString(16);}catch(e){} return String(a); }
var splashHwnd=null;
setTimeout(function(){
  var u=Process.findModuleByName('user32.dll');
  Interceptor.attach(u.findExportByName('CreateWindowExA'),{
    onEnter:function(a){ this.n=a[2]; try{ this.title=this.n.readAnsiString(); }catch(e){ this.title=''; } },
    onLeave:function(r){ if(this.title && this.title.indexOf('EFDC_Explore')>=0){ splashHwnd=r; send2('['+t()+'] splash hwnd='+r); } }
  });
  Interceptor.attach(u.findExportByName('DestroyWindow'),{
    onEnter:function(a){
      if(splashHwnd && a[0].equals(splashHwnd)) send2('['+t()+'] DestroyWindow(splash) from '+mod(this.returnAddress));
    }
  });
  var mb=Process.findModuleByName('msvbvm60.dll');
  send2('hooked');
}, 150);
send2('loaded');
