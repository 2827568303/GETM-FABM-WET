'use strict';
function send2(s){ send(s); }
var T0=Date.now(); function t(){ return ((Date.now()-T0)/1000).toFixed(2); }
var IID=[0x12,0x01,0,0,0,0,0,0,0xC0,0,0,0,0,0,0,0x46];
setTimeout(function(){
  try{
    var obj=ptr(0x16249b0).readPointer();
    send2('['+t()+'] obj='+obj);
    if(obj.isNull()) return;
    var vt=obj.readPointer();
    var QI=new NativeFunction(vt.readPointer(),'uint',['pointer','pointer','pointer']);
    var iid=Memory.alloc(16); iid.writeByteArray(new Uint8Array(IID));
    var pp=Memory.alloc(4);
    var hr=QI(obj,iid,pp);
    send2('['+t()+'] QI IOleObject hr=0x'+(hr>>>0).toString(16)+' p='+pp.readPointer());
    if((hr>>>0)!==0) return;
    var oo=pp.readPointer(); var ovt=oo.readPointer();
    var DoVerb=new NativeFunction(ovt.add(44).readPointer(),'uint',['pointer','int','pointer','pointer','uint','pointer','pointer']);
    var hr2=DoVerb(oo,-1,ptr(0),ptr(0),0,ptr(0),ptr(0));
    send2('['+t()+'] DoVerb hr=0x'+(hr2>>>0).toString(16));
  }catch(e){ send2('ERR '+e); }
}, 6500);
send2('loaded');
