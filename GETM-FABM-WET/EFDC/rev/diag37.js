'use strict';
// diag37.js — 原版 exe + 本地假服务器：追踪窗体显示与退出
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }

var u32 = Process.findModuleByName('user32.dll');
['ShowWindow','ShowWindowAsync','SetWindowPos'].forEach(function(n){
  var p = u32.findExportByName(n); if(!p) return;
  Interceptor.attach(p, { onEnter: function(a){
    if (n === 'SetWindowPos') return;
    emit(n + ' hwnd=' + a[0] + ' cmd=' + a[1].toInt32() + ' from ' + mod(this.returnAddress));
  }});
});
Interceptor.attach(u32.findExportByName('CreateWindowExW'), { onEnter: function(a){
  try{
    var cls = a[1].readUtf16String();
    if (/ThunderRT6/.test(cls)) emit('CreateWindow cls=' + cls + ' title=' + JSON.stringify(a[2].isNull()?'':a[2].readUtf16String()) + ' style=0x' + (a[3].toUInt32()>>>0).toString(16) + ' from ' + mod(this.returnAddress));
  }catch(e){}
}});
var pSoft = u32.findExportByName('SoftModalMessageBox');
Interceptor.attach(pSoft, { onEnter: function(a){
  try{
    var t = a[0].add(0xC).readPointer();
    emit('MsgBox text=' + JSON.stringify(t.isNull()?'':t.readUtf16String()));
  }catch(e){}
}});
var nt = Process.findModuleByName('ntdll.dll');
Interceptor.attach(nt.findExportByName('RtlExitUserProcess'), { onEnter: function(a){
  emit('EXIT code=' + a[0].toInt32() + ' from ' + mod(this.returnAddress));
  try{ emit('  ACC: ' + Thread.backtrace(this.context, Backtracer.ACCURATE).slice(0,14).map(mod).join(' <- ')); }catch(e){ emit('acc err'); } try{ emit('  FUZ: ' + Thread.backtrace(this.context, Backtracer.FUZZY).slice(0,24).map(mod).join(' <- ')); }catch(e){ emit('fuz err'); }
}});
emit('diag37 ready');

