'use strict';
function send2(s){ send(s); }
function sym(a){ try{ var m=Process.findModuleByAddress(ptr(a)); if(m) return m.name+'+0x'+(a-m.base).toString(16);}catch(e){} return null; }
setTimeout(function(){
  try{
    var th=Process.enumerateThreads()[0];
    var esp=th.context.esp;
    send2('main eip='+th.context.eip+' esp='+esp);
    var out=[];
    for(var o=0;o<0x1200;o+=4){
      try{
        var v=ptr(esp).add(o).readU32();
        var s=sym(v);
        if(s) out.push('+'+o.toString(16)+' '+v.toString(16)+' '+s);
      }catch(e){}
    }
    send2('stack:\n'+out.join('\n'));
  }catch(e){ send2('ERR '+e); }
}, 7000);
send2('loaded');
