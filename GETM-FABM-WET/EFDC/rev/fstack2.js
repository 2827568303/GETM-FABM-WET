'use strict';
function send2(s){ send(s); }
setTimeout(function(){
  try{
    var threads=Process.enumerateThreads();
    var main=threads[0];
    var c=main.context;
    var esp=c.esp; var eip=c.eip;
    send2('main tid='+main.id+' eip='+eip+' esp='+esp);
    var hits=[];
    for(var o=0;o<0x3000;o+=4){
      try{ var v=ptr(esp).add(o).readU32(); if(v>=0x401000 && v<0x1620000) hits.push('+'+o.toString(16)+':'+v.toString(16)); }catch(e){}
    }
    send2('stack code ptrs ('+hits.length+'): '+hits.slice(0,30).join(' '));
  }catch(e){ send2('ERR '+e); }
}, 7000);
send2('loaded');
