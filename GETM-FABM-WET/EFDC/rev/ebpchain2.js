'use strict';
function emit(s){ send(s); }
function mod(a){ try{ var m=Process.findModuleByAddress(ptr(a)); if(m) return m.name.replace('.dll','')+'+'+(a-m.base).toString(16);}catch(e){} return String(a); }
var IID=[0x81,0x09,0xF8,0x7B,0x32,0xBF,0x1A,0x10,0x8B,0xBB,0x00,0xAA,0x00,0x30,0x0C,0xAB];
setTimeout(function(){
  try{
    var oa=Process.findModuleByName('oleaut32.dll');
    var gdi=Process.findModuleByName('gdi32.dll');
    var CreateBitmap=new NativeFunction(gdi.findExportByName('CreateBitmap'),'pointer',['int','int','uint','uint','pointer']);
    var OleCreate=new NativeFunction(oa.findExportByName('OleCreatePictureIndirect'),'uint',['pointer','pointer','int','pointer']);
    var iid=Memory.alloc(16); iid.writeByteArray(new Uint8Array(IID));
    Interceptor.attach(oa.findExportByName('OleLoadPictureEx'),{
      onEnter:function(a){ this.ppv=a[7]; },
      onLeave:function(r){
        if((r.toInt32()>>>0)===0) return;
        try{ var hbmp=CreateBitmap(2,2,1,1,ptr(0));
          var desc=Memory.alloc(16); desc.writeU32(16); desc.add(4).writeU32(1); desc.add(8).writePointer(hbmp); desc.add(12).writePointer(ptr(0));
          if((OleCreate(desc,iid,1,this.ppv)>>>0)===0) r.replace(ptr(0)); }catch(e){}
      }
    });
  }catch(e){}
}, 200);
setTimeout(function(){
  try{
    var th=Process.enumerateThreads()[0];
    var ebp=th.context.ebp;
    var out=[];
    for(var i=0;i<20;i++){
      try{
        var ret=ebp.add(4).readU32();
        var next=ebp.readU32();
        out.push(i+':'+mod(ret));
        if(next<=ebp.toUInt32()) { out.push('(chain ends)'); break; }
        var np=ptr(next);
        ebp=np;
      }catch(e){ out.push('err '+e); break; }
    }
    emit('CHAIN: '+out.join(' | '));
  }catch(e){ emit('ERR '+e); }
}, 13000);
emit('loaded');
