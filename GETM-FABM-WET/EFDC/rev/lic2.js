'use strict';
function send2(s){ send(s); }
function gs(p){ try{ var b=new Uint8Array(p.readByteArray(16)); function h(x){return ('0'+x.toString(16)).slice(-2);}
 var d1=(b[3]<<24|b[2]<<16|b[1]<<8|b[0])>>>0, d2=(b[5]<<8|b[4]), d3=(b[7]<<8|b[6]), s='';
 for(var i=8;i<16;i++) s+=h(b[i]);
 return ('00000000'+d1.toString(16)).slice(-8)+'-'+('0000'+d2.toString(16)).slice(-4)+'-'+('0000'+d3.toString(16)).slice(-4)+'-'+s.substr(0,4)+'-'+s.substr(4); }catch(e){ return '?'; } }
var IMAGELIST='2c247f23-8591-11d1-b16a-00c0f0283628';
var done=false;
setTimeout(function(){
  try{
    var ole32=Process.findModuleByName('ole32.dll');
    Interceptor.attach(ole32.findExportByName('CoGetClassObject'),{
      onEnter:function(a){ this.c=gs(a[0]); this.ppv=a[4]; },
      onLeave:function(r){
        if(this.c!==IMAGELIST || (r.toInt32()>>>0)!==0 || done) return;
        try{
          var cf=this.ppv.readPointer(); var vt=cf.readPointer();
          var cfil=new NativeFunction(vt.add(16).readPointer(),'uint',['pointer','pointer','pointer','pointer','pointer']);
          var riid=Memory.alloc(16); riid.writeByteArray(new Uint8Array([0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xC0,0x00,0x00,0x00,0x00,0x00,0x00,0x46]));
          var pp=Memory.alloc(4);
          var hr=cfil(cf,ptr(0),riid,ptr(0),pp);
          var obj=pp.readPointer();
          send2('CreateInstanceLic hr=0x'+(hr>>>0).toString(16)+' obj='+obj);
          if(!obj.isNull()){
            done=true;
            var ovt=obj.readPointer();
            for(var i=3;i<=8;i++){
              (function(idx){
                var fn=ovt.add(idx*4).readPointer();
                Interceptor.attach(fn,{
                  onEnter:function(a){ this.idx=idx; },
                  onLeave:function(r){ send2('VCall['+idx+'] hr=0x'+((r.toInt32()>>>0).toString(16))); }
                });
              })(i);
            }
            send2('hooked object vtable 3..8');
          }
        }catch(e){ send2('err '+e); }
      }
    });
    send2('hooked');
  }catch(e){ send2('ERR '+e); }
}, 300);
send2('loaded');
