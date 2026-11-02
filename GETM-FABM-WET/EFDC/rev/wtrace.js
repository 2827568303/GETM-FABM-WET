'use strict';
function send2(s){ send(s); }
function wstr(p){ try{ return p.isNull()?'':p.readUtf16String(); }catch(e){ return '?'; } }
setTimeout(function(){
  var k=Process.findModuleByName('kernel32.dll');
  Interceptor.attach(k.findExportByName('CreateFileW'),{
    onEnter:function(a){
      var acc=a[1].toInt32(); var disp=a[4].toInt32();
      if(acc & 0x40000000){ this.p=wstr(a[0]); this.acc=acc; this.disp=disp; } // GENERIC_WRITE
    },
    onLeave:function(r){ if(this.p!==undefined) send2('WRITE-OPEN '+(r.toInt32()===-1?'FAIL':'ok')+' '+JSON.stringify(this.p)+' acc=0x'+this.acc.toString(16)+' disp='+this.disp); }
  });
  send2('hooked write-open');
}, 200);
send2('loaded');
