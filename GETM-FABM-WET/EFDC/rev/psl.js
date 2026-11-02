'use strict';
function send2(s){ send(s); }
function gb(s){ var m=s.replace(/[{}]/g,'').split('-'); var b=new Uint8Array(16);
  var d1=parseInt(m[0],16),d2=parseInt(m[1],16),d3=parseInt(m[2],16);
  b[0]=d1&255;b[1]=(d1>>8)&255;b[2]=(d1>>16)&255;b[3]=(d1>>>24)&255;
  b[4]=d2&255;b[5]=(d2>>8)&255;b[6]=d3&255;b[7]=(d3>>8)&255;
  for(var i=0;i<4;i++) b[8+i]=parseInt(m[3].substr(i*2,2),16);
  for(var i=0;i<8;i++) b[12+i]=parseInt(m[4].substr(i*2,2),16);
  return b; }
setTimeout(function(){
  try{
    var ole32=Process.findModuleByName('ole32.dll');
    var CCI=new NativeFunction(ole32.findExportByName('CoCreateInstance'),'uint',['pointer','pointer','uint','pointer','pointer']);
    var c=Memory.alloc(16); c.writeByteArray(gb('{2C247F23-8591-11D1-B16A-00C0F0283628}'));
    var iid=Memory.alloc(16); iid.writeByteArray(gb('{00000000-0000-0000-C000-000000000046}'));
    var pp=Memory.alloc(4);
    var hr=CCI(c,ptr(0),1,iid,pp);
    var obj=pp.readPointer();
    send2('CoCreateInstance hr=0x'+(hr>>>0).toString(16)+' obj='+obj);
    if(obj.isNull()) return;
    var ovt=obj.readPointer();
    var QI=new NativeFunction(ovt.add(0).readPointer(),'uint',['pointer','pointer','pointer']);
    var psIid=Memory.alloc(16); psIid.writeByteArray(gb('{00000109-0000-0000-C000-000000000046}'));
    var pps=Memory.alloc(4);
    var hr2=QI(obj,psIid,pps);
    var ps=pps.readPointer();
    send2('QI(IPersistStream) hr=0x'+(hr2>>>0).toString(16)+' ps='+ps);
    if(ps.isNull()) return;
    var pvt=ps.readPointer();
    var mod=Process.findModuleByName('mscomctl.ocx');
    for(var i=3;i<=7;i++){ var f=pvt.add(i*4).readPointer(); send2('PS slot '+i+' '+f+' rva='+f.sub(mod.base).toString(16)); }
    var load=pvt.add(5*4).readPointer();
    Interceptor.attach(load,{
      onEnter:function(a){ send2('Load called stm='+a[1]); },
      onLeave:function(r){ send2('Load hr=0x'+((r.toInt32()>>>0).toString(16))); }
    });
    send2('hooked Load');
  }catch(e){ send2('ERR '+e); }
}, 400);
send2('loaded');
