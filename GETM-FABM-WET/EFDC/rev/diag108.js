'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
var u32=Process.findModuleByName('user32.dll');
var GetWindowLongW=new NativeFunction(u32.findExportByName('GetWindowLongW'),'int',['pointer','int']);
var EnumWindows=new NativeFunction(u32.findExportByName('EnumWindows'),'int',['pointer','pointer']);
var GetClassNameW=new NativeFunction(u32.findExportByName('GetClassNameW'),'int',['pointer','pointer','int']);
var GetWindowTextW=new NativeFunction(u32.findExportByName('GetWindowTextW'),'int',['pointer','pointer','int']);
var GetWindowThreadProcessId=new NativeFunction(u32.findExportByName('GetWindowThreadProcessId'),'uint',['pointer','pointer']);
var myPid=Process.id;
Interceptor.attach(ptr(0x156ABE3), { onEnter: function(){
  var g=ptr(0x16204B4).readPointer();
  var s=ptr(0x16249B0).readPointer();
  emit('wizard obj=' + g + ' splash obj=' + s);
  var cb=new NativeCallback(function(h,l){
    var p=Memory.alloc(4); GetWindowThreadProcessId(h,p);
    if(p.readU32()!==myPid) return 1;
    var b=Memory.alloc(256); var n=GetClassNameW(h,b,200); var cls=n>0?b.readUtf16String(n):'';
    if(cls.indexOf('ThunderRT6Form')!==0) return 1;
    var tb=Memory.alloc(256); var tn=GetWindowTextW(h,tb,200); var t=tn>0?tb.readUtf16String(tn):'';
    emit('  hwnd='+h+' title='+JSON.stringify(t)+' userdata=0x'+(GetWindowLongW(h,-21)>>>0).toString(16));
    return 1;
  },'int',['pointer','pointer']);
  EnumWindows(cb,ptr(0));
}});
emit('ready');
