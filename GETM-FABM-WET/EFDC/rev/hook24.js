'use strict';
function send2(s){ send(s); }
var T0=Date.now(); function t(){ return ((Date.now()-T0)/1000).toFixed(2); }
function wstr(p){ try{ return p.isNull()?'':p.readUtf16String(); }catch(e){ return '<bad>'; } }
setTimeout(function(){
  try{
    Interceptor.attach(ptr(0x829650), { onEnter:function(a){ send2('['+t()+'] LOG '+JSON.stringify(wstr(a[0]))); } });
    send2('hooked log fn');
    // also mark success path entry
    Interceptor.attach(ptr(0x81CD9B), { onEnter:function(){ send2('['+t()+'] *** SUCCESS 0x81CD9B ***'); } });
    send2('hooked success');
    Interceptor.attach(ptr(0x828F50), { onEnter:function(){ send2('['+t()+'] *** form-init 0x828F50 ***'); } });
    send2('hooked forminit');
  }catch(e){ send2('err '+e); }
}, 200);
send2('loaded');
