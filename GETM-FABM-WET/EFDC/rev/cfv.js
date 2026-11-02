'use strict';
function send2(s){ send(s); }
function gs(p){ try{ var b=new Uint8Array(p.readByteArray(16)); function h(x){return ('0'+x.toString(16)).slice(-2);}
 var d1=(b[3]<<24|b[2]<<16|b[1]<<8|b[0])>>>0, d2=(b[5]<<8|b[4]), d3=(b[7]<<8|b[6]), s='';
 for(var i=8;i<16;i++) s+=h(b[i]);
 return ('00000000'+d1.toString(16)).slice(-8)+'-'+('0000'+d2.toString(16)).slice(-4)+'-'+('0000'+d3.toString(16)).slice(-4)+'-'+s.substr(0,4)+'-'+s.substr(4); }catch(e){ return '?'; } }
var IMAGELIST='2c247f23-8591-11d1-b16a-00c0f0283628'; var done=false;
setTimeout(function(){
  var ole32=Process.findModuleByName('ole32.dll');
  Interceptor.attach(ole32.findExportByName('CoGetClassObject'),{
    onEnter:function(a){ this.c=gs(a[0]); this.ppv=a[4]; },
    onLeave:function(r){
      if(this.c!==IMAGELIST || (r.toInt32()>>>0)!==0 || done) return; done=true;
      try{
        var cf=this.ppv.readPointer(); var cvt=cf.readPointer();
        var mod=Process.findModuleByName('mscomctl.ocx');
        for(var i=3;i<=7;i++){ var fn=cvt.add(i*4).readPointer(); send2('CF slot '+i+' = '+fn+' rva='+fn.sub(mod.base).toString(16)); }
      }catch(e){ send2('ERR '+e); }
    }
  });
  send2('hooked');
}, 300);
send2('loaded');
