'use strict';
function send2(s){ send(s); }
function wstr(p){ try{ return p.isNull()?'':p.readUtf16String(); }catch(e){ return '?'; } }
function mod(a){ try{ var m=Process.findModuleByAddress(a); if(m) return m.name+'+0x'+a.sub(m.base).toString(16);}catch(e){} return String(a); }
setTimeout(function(){
  var k=Process.findModuleByName('kernel32.dll');
  Interceptor.attach(k.findExportByName('CreateFileW'),{
    onEnter:function(a){ this.p=wstr(a[0]); },
    onLeave:function(r){ if(this.p && /\.(bmp|lic)/i.test(this.p)) send2('OPEN '+(r.toInt32()===-1?'FAIL':'ok')+' '+JSON.stringify(this.p)+' from '+mod(this.returnAddress)); }
  });
  Interceptor.attach(k.findExportByName('ReadFile'),{
    onLeave:function(r){ if(this.buf){ try{ var h=new Uint8Array(this.buf.readByteArray(16)); send2('READ '+(this.n||'?')+' '+Array.from(h).map(x=>x.toString(16).padStart(2,'0')).join('')); }catch(e){} } },
    onEnter:function(a){ this.buf=a[1]; this.n=a[2].toInt32(); }
  });
  send2('hooked');
}, 200);
send2('loaded');
