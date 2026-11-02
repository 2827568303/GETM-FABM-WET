'use strict';
function send2(s){ send(s); }
var T0=Date.now(); function t(){ return ((Date.now()-T0)/1000).toFixed(2); }
var done=false;
var IID_IDispatch=[0x00,0x04,0x02,0x00,0,0,0,0,0xC0,0,0,0,0,0,0,0x46];
function doShow(){
  try{
    var obj=ptr(0x16249b0).readPointer();
    send2('['+t()+'] obj='+obj);
    if(obj.isNull()) return;
    var vt=obj.readPointer();
    var QI=new NativeFunction(vt.readPointer(),'uint',['pointer','pointer','pointer']);
    var iid=Memory.alloc(16); iid.writeByteArray(new Uint8Array(IID_IDispatch));
    var pp=Memory.alloc(4);
    var hr=QI(obj,iid,pp);
    send2('['+t()+'] QI hr=0x'+(hr>>>0).toString(16));
    if((hr>>>0)!==0) return;
    var disp=pp.readPointer(); var dvt=disp.readPointer();
    var GetIDsOfNames=new NativeFunction(dvt.add(20).readPointer(),'uint',['pointer','pointer','pointer','uint','uint','pointer']);
    var Invoke=new NativeFunction(dvt.add(24).readPointer(),'uint',['pointer','int','pointer','uint','int','pointer','pointer','pointer','pointer']);
    var nb=Memory.allocUtf16String('Show');
    var names=Memory.alloc(Process.pointerSize); names.writePointer(nb);
    var dispid=Memory.alloc(4); var nil=Memory.alloc(16);
    var h1=GetIDsOfNames(disp,nil,names,1,0,dispid);
    send2('['+t()+'] GetIDsOfNames hr=0x'+(h1>>>0).toString(16)+' id='+dispid.readInt32());
    if((h1>>>0)!==0) return;
    var prm=Memory.alloc(24); prm.writePointer(ptr(0)); prm.add(8).writePointer(ptr(0)); prm.add(16).writeInt32(0); prm.add(20).writeInt32(0);
    var res=Memory.alloc(16);
    var h2=Invoke(disp,dispid.readInt32(),nil,1,2,prm,res,ptr(0),ptr(0));
    send2('['+t()+'] Invoke(Show) hr=0x'+(h2>>>0).toString(16));
  }catch(e){ send2('doShow ERR '+e); }
}
setTimeout(function(){
  var u=Process.findModuleByName('user32.dll');
  ['GetMessageA','GetMessageW','PeekMessageA','PeekMessageW'].forEach(function(fn){
    var p=u.findExportByName(fn); if(!p) return;
    try{ Interceptor.attach(p,{ onEnter:function(){ if(!done && (Date.now()-T0)>5500){ done=true; send2('['+t()+'] via '+fn); doShow(); } } }); send2('hooked '+fn); }catch(e){ send2('fail '+fn); }
  });
}, 150);
send2('loaded');
