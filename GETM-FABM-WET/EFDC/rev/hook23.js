'use strict';
function send2(s){ send(s); }
var T0=Date.now(); function t(){ return ((Date.now()-T0)/1000).toFixed(2); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); if(m) return m.name+'+0x'+a.sub(m.base).toString(16);}catch(e){} return String(a); }
setTimeout(function(){
  try{
    var m=Process.findModuleByName('oleaut32.dll');
    var p=m.findExportByName('OleLoadPictureEx');
    send2('oleaut32 base='+m.base+' ex='+p+' head='+Array.from(new Uint8Array(p.readByteArray(10))).map(function(b){return ('0'+b.toString(16)).slice(-2);}).join(''));
    var rel=p.add(6).readS32();
    var tgt=p.add(10).add(rel);
    send2('call target='+tgt+' ('+mod(tgt)+')');
    Interceptor.attach(tgt,{
      onEnter:function(a){ send2('['+t()+'] ENTER tgt a0='+a[0]+' a1='+a[1]+' a2='+a[2]+' a3='+a[3]); },
      onLeave:function(r){ send2('['+t()+'] LEAVE tgt ret='+r); }
    });
    // also trace this target's first call target
    try{
      var b=tgt.readByteArray(12);
      send2('tgt head='+Array.from(new Uint8Array(b)).map(function(x){return ('0'+x.toString(16)).slice(-2);}).join(''));
    }catch(e){}
  }catch(e){ send2('err '+e); }
}, 300);
send2('loaded');
