'use strict';
function emit(s){ send(s); }
var IID=[0x81,0x09,0xF8,0x7B,0x32,0xBF,0x1A,0x10,0x8B,0xBB,0x00,0xAA,0x00,0x30,0x0C,0xAB];
var done=false;
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
    var u=Process.findModuleByName('user32.dll');
    ['PeekMessageW','PeekMessageA','GetMessageW','GetMessageA','DispatchMessageA','DispatchMessageW'].forEach(function(fname){
    var pm=u.findExportByName(fname); if(!pm) return;
    Interceptor.attach(pm,{
      onEnter:function(){
        if(done) return;
        try{
          var obj=ptr(0x16249b0).readPointer();
          if(obj.isNull()) return;
          done=true;
          emit('main-thread: form obj='+obj);
          var vt=obj.readPointer();
          [0x94,0x6e*4,0x1b8].forEach(function(off){
            try{
              var f=vt.add(off).readPointer();
              var fn=new NativeFunction(f,'uint',['pointer','int']);
              var hr=fn(obj,-1);
              emit('  call slot 0x'+off.toString(16)+' -> 0x'+(hr>>>0).toString(16));
            }catch(e){ emit('  slot 0x'+off.toString(16)+' err '+e); }
          });
        }catch(e){ emit('peek err '+e); }
      }
    });
    });
    emit('ready');
  }catch(e){ emit('ERR '+e); }
}, 200);
emit('loaded');
