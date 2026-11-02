'use strict';
function send2(s){ send(s); }
setTimeout(function(){
  try{
    var threads=Process.enumerateThreads();
    send2('threads: '+threads.length);
    threads.forEach(function(th){
      var c=th.context;
      var eip=c.eip?c.eip.toUInt32():0, esp=c.esp?c.esp.toUInt32():0, ebp=c.ebp?c.ebp.toUInt32():0;
      send2('tid='+th.id+' state='+th.state+' eip=0x'+eip.toString(16)+' esp=0x'+esp.toString(16)+' ebp=0x'+ebp.toString(16));
      if(!esp) return;
      try{
        var data=new Uint8Array(Memory.readByteArray(ptr(esp),0x4000));
        var hits=[];
        for(var o=0;o<data.length-4;o+=4){
          var v=(data[o]|(data[o+1]<<8)|(data[o+2]<<16)|(data[o+3]<<24))>>>0;
          if(v>=0x401000 && v<0x1620000) hits.push('+'+(o).toString(16)+':'+v.toString(16));
        }
        send2('  stack code ptrs ('+hits.length+'): '+hits.slice(0,25).join(' '));
      }catch(e){ send2('  read err '+e); }
    });
  }catch(e){ send2('ERR '+e); }
}, 7000);
send2('loaded');
