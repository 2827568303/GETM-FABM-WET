'use strict';
function send2(s){ send(s); }
setTimeout(function(){
  try{
    var obj=ptr(0x16249b0).readPointer();
    if(obj.isNull()){ send2('null obj'); return; }
    var vt=obj.readPointer();
    send2('vtable='+vt);
    var out=[];
    for(var i=0;i<0x200;i+=4){
      var fn=vt.add(i).readPointer();
      var n=fn.toUInt32 ? fn.toUInt32() : 0;
      if(n>=0x401000 && n<0x1620000) out.push(i+':'+n.toString(16));
    }
    send2('exe-ptrs: '+out.join(' '));
  }catch(e){ send2('ERR '+e); }
}, 6200);
send2('loaded');
