'use strict';
function send2(s){ send(s); }
function sym(a){ try{ var m=Process.findModuleByAddress(ptr(a)); if(m) return m.name.replace('.dll','')+'+'+(a-m.base).toString(16);}catch(e){} return null; }
setTimeout(function(){
  try{
    var ths=Process.enumerateThreads();
    send2('threads='+ths.length);
    ths.forEach(function(th,i){
      var eip=th.context.eip.toUInt32();
      var esp=th.context.esp.toUInt32();
      var chain=[];
      for(var o=0;o<0x800 && chain.length<6;o+=4){
        try{ var v=ptr(esp).add(o).readU32(); var s=sym(v); if(s && !s.startsWith('ntdll') ) chain.push(s); }catch(e){}
      }
      send2('T'+(i+1)+' '+sym(eip)+' :: '+chain.join(' <- '));
    });
  }catch(e){ send2('ERR '+e); }
}, 6500);
send2('loaded');
