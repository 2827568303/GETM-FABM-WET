'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
var u32=Process.findModuleByName('user32.dll');
var GetClassNameW=new NativeFunction(u32.findExportByName('GetClassNameW'),'int',['pointer','pointer','int']);
Interceptor.attach(u32.findExportByName('ShowWindow'),{
  onEnter:function(a){
    var cls='';
    try{ var b=Memory.alloc(256); var n=GetClassNameW(a[0],b,200); cls=n>0?b.readUtf16String(n):''; }catch(e){}
    if(cls.indexOf('ThunderRT6Form')===0) emit('ShowWindow('+a[0]+', '+a[1].toInt32()+') cls='+cls);
  }
});
emit('ready');
