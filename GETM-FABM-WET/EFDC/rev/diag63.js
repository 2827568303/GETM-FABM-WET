'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
var u32=Process.findModuleByName('user32.dll');
var GetClassNameW=new NativeFunction(u32.findExportByName('GetClassNameW'),'int',['pointer','pointer','int']);
var n=0;
Interceptor.attach(u32.findExportByName('CreateWindowExA'),{
  onEnter:function(a){ try{ this.cls=a[1].readAnsiString(); }catch(e){ this.cls=null; } },
  onLeave:function(r){
    n++;
    var real='';
    try{ var b=Memory.alloc(256); var k=GetClassNameW(r,b,200); real = k>0? b.readUtf16String(k):''; }catch(e){}
    if (n<=60) emit('W['+n+'] cls_arg=' + (this.cls||'<atom>') + '  real=' + real);
  }
});
emit('ready');
