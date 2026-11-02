'use strict';
function send2(s){ send(s); }
function wstr(p){ try{ return p.isNull()?'':p.readUtf16String(); }catch(e){ return '?'; } }
function mod(a){ try{ var m=Process.findModuleByAddress(a); if(m) return m.name+'+0x'+a.sub(m.base).toString(16);}catch(e){} return String(a); }
setTimeout(function(){
  var k=Process.findModuleByName('kernel32.dll');
  Interceptor.attach(k.findExportByName('CreateFileW'),{
    onEnter:function(a){ this.p=wstr(a[0]); },
    onLeave:function(r){
      if(this.p && /license/i.test(this.p)){
        send2('LICFILE '+JSON.stringify(this.p)+' -> '+(r.toInt32()===-1?'FAIL':'ok')+' from '+mod(this.returnAddress));
        send2('  stack: '+Thread.backtrace(this.context,Backtracer.FUZZY).map(function(x){return mod(x);}).filter(function(x){return x.indexOf('EFDC')>=0;}).slice(0,5).join(' <- '));
      }
    }
  });
  send2('hooked');
}, 200);
send2('loaded');
