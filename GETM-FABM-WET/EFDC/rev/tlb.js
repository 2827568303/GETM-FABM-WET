'use strict';
function send2(s){ send(s); }
function rstr(p){ try{ return p.isNull()?'':p.readUtf16String(); }catch(e){ return ''; } }
setTimeout(function(){
  try{
    var oa=Process.findModuleByName('oleaut32.dll');
    var LoadTypeLib=new NativeFunction(oa.findExportByName('LoadTypeLib'),'uint',['pointer','pointer']);
    var p=Memory.alloc(600); p.writeUtf16String('C:\\Users\\23801\\Desktop\\GETM-FABM-WET-260928\\GETM-FABM-WET\\EFDC\\EFDC \u5546\u4e1a\u72488.4\\EFDC_Explorer8.4.exe');
    var out=Memory.alloc(4);
    var hr=LoadTypeLib(p,out);
    send2('LoadTypeLib hr=0x'+(hr>>>0).toString(16));
    if((hr>>>0)!==0) return;
    var tl=out.readPointer(); var vt=tl.readPointer();
    var GetCount=new NativeFunction(vt.add(12).readPointer(),'uint',['pointer']);
    var GetTI=new NativeFunction(vt.add(16).readPointer(),'uint',['pointer','uint','pointer']);
    var GetTIT=new NativeFunction(vt.add(20).readPointer(),'uint',['pointer','uint','pointer']);
    var n=GetCount(tl);
    send2('type count='+n);
    var names=[];
    for(var i=0;i<n;i++){
      var kind=Memory.alloc(4);
      if(GetTIT(tl,i,kind)!==0) continue;
      var ti=Memory.alloc(4);
      if(GetTI(tl,i,ti)!==0) continue;
      var info=ti.readPointer(); var ivt=info.readPointer();
      var GetDoc=new NativeFunction(ivt.add(48).readPointer(),'uint',['pointer','int','pointer','pointer','pointer','pointer']);
      var nm=Memory.alloc(4),doc=Memory.alloc(4),hf=Memory.alloc(4),cx=Memory.alloc(4);
      if(GetDoc(info,-1,nm,doc,hf,cx)===0){
        var s=rstr(nm.readPointer());
        if(s) names.push(s+'('+kind.readU32()+')');
      }
    }
    send2('types: '+names.join(', '));
  }catch(e){ send2('ERR '+e); }
}, 1200);
send2('loaded');
