'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }
function bstr(p){ try{ return p.isNull()?'':p.readUtf16String(); }catch(e){ return ''; } }
Interceptor.attach(ptr(0x829650), { onEnter: function(a){
  var s1=bstr(a[0]), s2=bstr(a[1]);
  emit('LOG caller=' + mod(this.returnAddress) + '  a0=' + JSON.stringify(s1) + '  a1=' + JSON.stringify(s2));
}});
emit('ready');
