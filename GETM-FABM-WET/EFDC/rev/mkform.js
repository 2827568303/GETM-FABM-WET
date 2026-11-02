'use strict';
function send2(s){ send(s); }
setTimeout(function(){
  try{
    var mb=Process.findModuleByName('msvbvm60.dll');
    var New2=new NativeFunction(mb.findExportByName('__vbaNew2'),'uint',['pointer','pointer']);
    var out=Memory.alloc(16);
    var infos=[0x4DF87C,0x4DF888,0x4DF880,0x4DED9C,0x4DED94,0x4DD92C];
    infos.forEach(function(va){
      var p=Memory.alloc(16); p.writeU64(0); p.add(8).writeU64(0);
      try{
        var hr=New2(p, ptr(va));
        var obj=p.readPointer();
        send2('New2(0x'+va.toString(16)+') hr=0x'+(hr>>>0).toString(16)+' obj='+obj);
      }catch(e){ send2('New2(0x'+va.toString(16)+') threw '+e); }
    });
  }catch(e){ send2('ERR '+e); }
}, 2500);
send2('loaded');
