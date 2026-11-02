'use strict';
function send2(s){ send(s); }
function gs(p){ try{ var b=new Uint8Array(p.readByteArray(16)); function h(x){return ('0'+x.toString(16)).slice(-2);}
 var d1=(b[3]<<24|b[2]<<16|b[1]<<8|b[0])>>>0, d2=(b[5]<<8|b[4]), d3=(b[7]<<8|b[6]), s='';
 for(var i=8;i<16;i++) s+=h(b[i]);
 return ('00000000'+d1.toString(16)).slice(-8)+'-'+('0000'+d2.toString(16)).slice(-4)+'-'+('0000'+d3.toString(16)).slice(-4)+'-'+s.substr(0,4)+'-'+s.substr(4); }catch(e){ return '?'; } }
setTimeout(function(){
  try{
    var ole32=Process.findModuleByName('ole32.dll');
    ['CoGetClassObject','CoCreateInstanceEx','CoLoadLibrary'].forEach(function(fn){
      var p=ole32.findExportByName(fn); if(!p) return;
      Interceptor.attach(p,{
        onEnter:function(a){ this.c=gs(a[0]); },
        onLeave:function(r){ var hr=r.toInt32()>>>0; send2(fn+' '+this.c+' hr=0x'+hr.toString(16)); }
      });
      send2('hooked '+fn);
    });
  }catch(e){ send2('ERR '+e); }
}, 300);
send2('loaded');
