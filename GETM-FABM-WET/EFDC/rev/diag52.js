'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }
var vb = Process.findModuleByName('MSVBVM60.DLL');
var seen={};
Interceptor.attach(vb.findExportByName('__vbaFileOpen'), { onEnter: function(a){
  var p=''; try{ p=a[3].readUtf16String(); }catch(e){}
  if (p.indexOf('ee_activation.log')<0) return;
  var ra = mod(this.returnAddress);
  if (!seen[ra]) { seen[ra]=1; emit('LOGWRITE caller=' + ra + '  from ' + mod(this.returnAddress)); }
}});
emit('ready');
