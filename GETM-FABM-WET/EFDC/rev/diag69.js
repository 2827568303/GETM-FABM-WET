'use strict';
function emit(s){ send(s); }
var vb=Process.findModuleByName('MSVBVM60.DLL');
Interceptor.attach(vb.findExportByName('__vbaNew2'),{
  onEnter:function(a){ this.out=a[1]; this.ci=a[0]; },
  onLeave:function(){
    try{ if((this.ci.toInt32()>>>0)!==0x4D5204) return; }catch(e){ return; }
    var obj; try{ obj=this.out.readPointer(); }catch(e){ return; }
    if(obj.isNull()) return;
    var vt=obj.readPointer();
    [0x94,0x1b8,0x250].forEach(function(off){
      try{
        var p=vt.add(off).readPointer();
        var rel=p.add(1).readS32();
        var tgt=p.add(5).add(rel);
        var b=new Uint8Array(tgt.readByteArray(16));
        emit('slot 0x'+off.toString(16)+' stub -> '+tgt+' : '+Array.from(b).map(function(x){return x.toString(16).padStart(2,'0');}).join(' '));
      }catch(e){ emit('slot 0x'+off.toString(16)+' err '+e); }
    });
  }
});
emit('ready');
