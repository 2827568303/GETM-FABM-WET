'use strict';
function emit(s){ send(s); }
function wstr(p){ try{ return p.isNull()?'':p.readUtf16String(); }catch(e){ return '?'; } }
function astr(p){ try{ return p.isNull()?'':p.readAnsiString(); }catch(e){ return '?'; } }
setTimeout(function(){
  try{
    var k=Process.findModuleByName('kernel32.dll');
    Interceptor.attach(k.findExportByName('CreateFileW'),{
      onEnter:function(a){ this.p=wstr(a[0]); this.w=(a[1].toInt32()&0x40000000)!==0; },
      onLeave:function(r){ emit((this.w?'WRITE-OPEN ':'open ')+(r.toInt32()===-1?'FAIL':'ok')+' '+JSON.stringify(this.p)); }
    });
    var adv=Process.findModuleByName('advapi32.dll');
    if(adv){
      var rs=adv.findExportByName('RegSetValueExW');
      if(rs) Interceptor.attach(rs,{ onEnter:function(a){ emit('RegSet '+JSON.stringify(wstr(a[1]))); } });
      var ro=adv.findExportByName('RegCreateKeyExW');
      if(ro) Interceptor.attach(ro,{ onEnter:function(a){ emit('RegCreate '+JSON.stringify(wstr(a[1]))); } });
    }
    emit('hooked');
  }catch(e){ emit('ERR '+e); }
}, 100);
emit('loaded');
