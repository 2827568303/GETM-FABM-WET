'use strict';
function emit(s){ send(s); }
var T0=Date.now(); function t(){ return ((Date.now()-T0)/1000).toFixed(2); }
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
  [[0x81D3E0,'FNO'],[0x81D991,'Kill'],[0x81D870,'WarnBuilder'],[0x156AB70,'ActUI'],[0x156ACC0,'TitleInit'],[0x81C922,'ActGate'],[0x81CD9B,'Success'],[0x828F50,'SplashInit']].forEach(function(p){
    try{ Interceptor.attach(ptr(p[0]),{ onEnter:function(){ emit('['+t()+'] '+p[1]); } }); }catch(e){}
  });
  emit('hooked');
}, 200);
emit('loaded');
