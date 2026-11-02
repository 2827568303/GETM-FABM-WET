'use strict';
function emit(s){ send(s); }
function wstr(p){ try{ return p.isNull()?'':p.readUtf16String(); }catch(e){ return '?'; } }
try{
  var k=Module.findExportByName('kernel32.dll','CreateFileW');
  Interceptor.attach(k,{
    onEnter:function(a){ this.p=wstr(a[0]); this.w=(a[1].toInt32()&0x40000000)!==0; },
    onLeave:function(r){ emit((this.w?'WRITE ':'open ')+(r.toInt32()===-1?'FAIL':'ok')+' '+JSON.stringify(this.p)); }
  });
  var rs=Module.findExportByName('advapi32.dll','RegSetValueExW');
  if(rs) Interceptor.attach(rs,{ onEnter:function(a){ emit('RegSetValue '+JSON.stringify(wstr(a[1]))); } });
  var rc=Module.findExportByName('advapi32.dll','RegCreateKeyExW');
  if(rc) Interceptor.attach(rc,{ onEnter:function(a){ emit('RegCreateKey '+JSON.stringify(wstr(a[1]))); } });
  emit('hooked immediately');
}catch(e){ emit('ERR '+e); }
