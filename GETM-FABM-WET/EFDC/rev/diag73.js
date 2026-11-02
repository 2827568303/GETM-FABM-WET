'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function hook(a,n){ try{ Interceptor.attach(ptr(parseInt(a,16)), { onEnter:function(){ emit('HIT '+n); }, onLeave:function(r){ emit('  leave '+n+' ret='+r.toInt32()); } }); }catch(e){ emit('fail '+n); } }
hook('0x156AC31','call [obj48FE70+0x2B0]');
hook('0x156AC4D','create 0x48FE70');
hook('0x156AC3F','skip-branch');
var u32=Process.findModuleByName('user32.dll');
var EnumWindows=new NativeFunction(u32.findExportByName('EnumWindows'),'int',['pointer','pointer']);
var GetClassNameW=new NativeFunction(u32.findExportByName('GetClassNameW'),'int',['pointer','pointer','int']);
var IsWindowVisible=new NativeFunction(u32.findExportByName('IsWindowVisible'),'int',['pointer']);
var GetWindowThreadProcessId=new NativeFunction(u32.findExportByName('GetWindowThreadProcessId'),'uint',['pointer','pointer']);
var myPid=Process.id;
function list(tag){
  var out=[];
  var cb=new NativeCallback(function(h,l){
    var p=Memory.alloc(4); GetWindowThreadProcessId(h,p);
    if(p.readU32()!==myPid) return 1;
    var b=Memory.alloc(256); var n=GetClassNameW(h,b,200); var cls=n>0?b.readUtf16String(n):'';
    if(cls.indexOf('Thunder')===0) out.push(cls+'|vis='+IsWindowVisible(h));
    return 1;
  },'int',['pointer','pointer']);
  EnumWindows(cb,ptr(0));
  emit('  ['+tag+'] '+(out.length?out.join(' ;; '):'<none>'));
}
setTimeout(function(){ list('+2s'); }, 2000);
setTimeout(function(){ list('+6s'); }, 6000);
emit('ready');
