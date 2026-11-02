'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }
var k32=Process.findModuleByName('kernel32.dll');
var n=0;
Interceptor.attach(k32.findExportByName('RaiseException'),{onEnter:function(a){
  if((a[0].toUInt32()>>>0)!==0xc000008f) return;
  var t=Date.now()-t0; if(t<3000) return;
  n++;
  emit('VBERR @'+t+' from '+mod(this.returnAddress));
  try{ emit('  '+Thread.backtrace(this.context, Backtracer.FUZZY).slice(0,20).map(mod).join(' <- ')); }catch(e){}
}});
var u32=Process.findModuleByName('user32.dll');
Interceptor.attach(u32.findExportByName('SoftModalMessageBox'),{onEnter:function(){ emit('MSGBOX @'+(Date.now()-t0)); }});
emit('ready');
