'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function guid(p){
  try{ var b=new Uint8Array(p.readByteArray(16));
    var d1=(b[0]|b[1]<<8|b[2]<<16|b[3]<<24)>>>0;
    var s=d1.toString(16).padStart(8,'0')+'-'+b[4].toString(16).padStart(2,'0')+b[5].toString(16).padStart(2,'0')+'-'+b[6].toString(16).padStart(2,'0')+b[7].toString(16).padStart(2,'0')+'-';
    for(var i=8;i<10;i++) s+=b[i].toString(16).padStart(2,'0');
    s+='-'; for(var i=10;i<16;i++) s+=b[i].toString(16).padStart(2,'0');
    return s;
  }catch(e){ return '?'; }
}
var ol=Process.findModuleByName('ole32.dll');
['CoCreateInstance','CoCreateInstanceEx','CoGetClassObject'].forEach(function(n){
  var p=ol.findExportByName(n); if(!p) return;
  Interceptor.attach(p,{onEnter:function(a){ emit(n+' clsid={'+guid(a[0])+'}'); }});
});
emit('ready');
