'use strict';
function emit(s){ send(s); }
function wstr(p){ try{ return p.isNull()?'':p.readUtf16String(); }catch(e){ return '?'; } }
try{
  var km=Process.findModuleByName('kernel32.dll');
  var k=km.findExportByName('CreateFileW');
  Interceptor.attach(k,{
    onEnter:function(a){ this.p=wstr(a[0]); this.w=(a[1].toInt32()&0x40000000)!==0; },
    onLeave:function(r){ emit((this.w?'WRITE ':'open ')+(r.toInt32()===-1?'FAIL':'ok')+' '+JSON.stringify(this.p)); }
  });
  emit('hooked CreateFileW at '+k);
}catch(e){ emit('ERR1 '+e); }
try{
  var am=Process.findModuleByName('advapi32.dll');
  if(am){
    var rs=am.findExportByName('RegSetValueExW');
    if(rs) Interceptor.attach(rs,{ onEnter:function(a){ emit('RegSetValue '+JSON.stringify(wstr(a[1]))); } });
    emit('hooked registry');
  }
}catch(e){ emit('ERR2 '+e); }
