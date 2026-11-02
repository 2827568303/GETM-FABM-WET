'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
Interceptor.attach(ptr(0x81D0D3), { onEnter: function(){
  var p=ptr(0x4016A4).readPointer();
  var m=Process.findModuleByAddress(p);
  var name='?';
  if(m){ try{ var ex=m.enumerateExports(); for(var i=0;i<ex.length;i++){ if(ex[i].address.equals(p)){ name=ex[i].name; break; } } }catch(e){} }
  emit('[0x4016A4] = '+p+'  module='+(m?m.name:'?')+'  export='+name);
}});
emit('ready');
