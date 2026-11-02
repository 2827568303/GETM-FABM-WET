'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
var vb=Process.findModuleByName('MSVBVM60.DLL');
Interceptor.attach(vb.findExportByName('__vbaNew2'),{
  onEnter:function(a){ this.out=a[1]; this.ci=a[0]; },
  onLeave:function(){
    try{ if((this.ci.toInt32()>>>0)!==0x4D5204) return; }catch(e){ return; }
    var obj; try{ obj=this.out.readPointer(); }catch(e){ return; }
    if(obj.isNull()) return;
    var vt=obj.readPointer();
    emit('vtable='+vt);
    [0x94,0x1b8,0x1bc,0x250,0x310,0x18].forEach(function(off){
      try{
        var p=vt.add(off).readPointer();
        var b=new Uint8Array(p.readByteArray(12));
        var hex=Array.from(b).map(function(x){return x.toString(16).padStart(2,'0');}).join(' ');
        emit('  slot 0x'+off.toString(16)+' -> '+p+'  bytes: '+hex);
      }catch(e){ emit('  slot 0x'+off.toString(16)+' err'); }
    });
  }
});
emit('ready');
