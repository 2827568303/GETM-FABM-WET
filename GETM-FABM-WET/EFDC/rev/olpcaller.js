'use strict';
function send2(s){ send(s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); if(m) return m.name+'+0x'+a.sub(m.base).toString(16);}catch(e){} return String(a); }
setTimeout(function(){
  var oa=Process.findModuleByName('oleaut32.dll');
  var p=oa.findExportByName('OleLoadPictureEx');
  send2('target='+p+' ('+mod(p)+')');
  Interceptor.attach(p,{
    onEnter:function(a){ send2('call from '+mod(this.returnAddress)+' args '+a[0]+' '+a[1]+' '+a[2]+' '+a[3]+' '+a[4]+' '+a[5]+' '+a[6]); }
  });
  send2('hooked');
}, 200);
send2('loaded');
