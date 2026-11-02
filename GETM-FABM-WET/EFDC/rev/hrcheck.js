'use strict';
function send2(s){ send(s); }
var T0=Date.now(); function t(){ return ((Date.now()-T0)/1000).toFixed(2); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); if(m) return m.name+'+0x'+a.sub(m.base).toString(16);}catch(e){} return String(a); }
setTimeout(function(){
  var mb=Process.findModuleByName('msvbvm60.dll');
  var p=mb.findExportByName('__vbaHresultCheckObj');
  send2('HresultCheckObj at '+p);
  Interceptor.attach(p,{
    onEnter:function(a){ this.hr=a[0].toInt32(); this.obj=a[1]; this.off=a[2].toInt32(); this.from=this.returnAddress; },
    onLeave:function(){
      var f=mod(this.from);
      send2('['+t()+'] HResult hr=0x'+((this.hr>>>0).toString(16))+' off=0x'+this.off.toString(16)+' from='+f);
    }
  });
  send2('hooked');
}, 200);
send2('loaded');
