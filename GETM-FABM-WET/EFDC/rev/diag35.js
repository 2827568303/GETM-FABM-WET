'use strict';
// diag35.js — 跳过 CheckLicensing，看 Sub Main 是否继续创建窗体
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }

try {
  Interceptor.replace(ptr(0x81C4C0), new NativeCallback(function(){
    emit('CheckLicensing 被跳过（直接返回）');
  }, 'void', []));
  emit('CheckLicensing replaced');
} catch (e) { emit('replace fail ' + e); }

['0x828F50','0x156ACC0'].forEach(function(a){
  var p = ptr(parseInt(a, 16));
  try {
    Interceptor.attach(p, {
      onEnter: function(){ emit('ENTER ' + a); },
      onLeave: function(){ emit('LEAVE ' + a); }
    });
  } catch (e) { emit('attach fail ' + a + ': ' + e); }
});

var u32 = Process.findModuleByName('user32.dll');
Interceptor.attach(u32.findExportByName('CreateWindowExW'), { onEnter: function(a){
  try{
    var cls = a[1].readUtf16String();
    if (/ThunderRT6/.test(cls)) emit('CreateWindow cls=' + cls + ' title=' + JSON.stringify(a[2].isNull()?'':a[2].readUtf16String()) + ' style=0x' + (a[3].toUInt32()>>>0).toString(16));
  }catch(e){}
}});
emit('diag35 ready');
