'use strict';
function send2(s){ send(s); }
setTimeout(function(){
  try{
    var oa=Process.findModuleByName('oleaut32.dll');
    Interceptor.attach(oa.findExportByName('OleLoadPictureEx'),{
      onEnter:function(a){ this.stm=a[0]; this.size=a[1].toInt32(); this.run=a[2].toInt32(); this.cx=a[3].toInt32(); this.cy=a[4].toInt32(); this.flags=a[5].toInt32(); this.out=a[6]; },
      onLeave:function(r){
        var st='?';
        try{
          var vt=this.stm.readPointer(); var Stat=new NativeFunction(vt.add(12).readPointer(),'uint',['pointer','pointer']);
          var s=Memory.alloc(32); var hr=Stat(this.stm,s);
          st='stat hr=0x'+(hr>>>0).toString(16)+' type='+s.readU32()+' size='+(s.add(8).readU32()|0)+' cbSize='+s.add(8).readU32();
        }catch(e){ st='stat err '+e; }
        send2('OleLoadPictureEx(stm='+this.stm+' size='+this.size+' run='+this.run+' cx='+this.cx+' cy='+this.cy+' flags=0x'+this.flags.toString(16)+') hr=0x'+(r.toInt32()>>>0).toString(16)+' | '+st);
      }
    });
  }catch(e){ send2('ERR '+e); }
}, 1500);
send2('loaded');
