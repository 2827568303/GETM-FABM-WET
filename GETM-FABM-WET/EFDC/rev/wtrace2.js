'use strict';
function send2(s){ send(s); }
function wstr(p){ try{ return p.isNull()?'':p.readUtf16String(); }catch(e){ return '?'; } }
setTimeout(function(){
  var k=Process.findModuleByName('kernel32.dll');
  var GetLastError=new NativeFunction(k.findExportByName('GetLastError'),'uint',[]);
  Interceptor.attach(k.findExportByName('CreateFileW'),{
    onEnter:function(a){
      this.p=wstr(a[0]); this.acc=a[1].toInt32(); this.share=a[2].toInt32();
      this.sa=a[3]; this.disp=a[4].toInt32(); this.flags=a[5].toInt32();
    },
    onLeave:function(r){
      if(r.toInt32()!==-1) return;
      var e=GetLastError();
      send2('FAIL err='+e+' path='+JSON.stringify(this.p)+' acc=0x'+(this.acc>>>0).toString(16)+' share='+this.share+' sa='+this.sa+' disp='+this.disp+' flags=0x'+this.flags.toString(16));
    }
  });
  send2('hooked');
}, 200);
send2('loaded');
