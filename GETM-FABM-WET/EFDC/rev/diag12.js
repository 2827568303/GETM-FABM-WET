'use strict';
// diag12.js — 观察窗体创建与启动流程（配合 C:\EFDC84_RUN 副本）
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }
function hx(v){ return ('00000000'+(v>>>0).toString(16)).slice(-8); }

var vb = Process.findModuleByName('MSVBVM60.DLL');
if (vb) {
  var pNew2 = vb.findExportByName('__vbaNew2');
  if (pNew2) Interceptor.attach(pNew2, { onEnter: function(a){
    var ci = a[0];
    var s = '';
    try{ s = ' +4=' + hx(ci.add(4).readU32()) + ' +18=' + hx(ci.add(0x18).readU32()); }catch(e){}
    emit('__vbaNew2 classinfo=' + ci + s + ' from ' + mod(this.returnAddress));
  }});
  ['__vbaNew','__vbaNew3'].forEach(function(n){ var p = vb.findExportByName(n); if(p) Interceptor.attach(p, { onEnter: function(a){ emit(n+' classinfo='+a[0]); }}); });
}

function hookFlow(addr, name){
  Interceptor.attach(ptr(addr), { onEnter: function(){ emit('ENTER ' + name); }, onLeave: function(r){ emit('LEAVE ' + name); } });
}
hookFlow(0x81C4C0, 'CheckLicensing');
hookFlow(0x828F50, 'SplashInit');
hookFlow(0x156ACC0, 'TitleInit');
hookFlow(0x156AD58, 'PushClassInfoSite');

var u32 = Process.findModuleByName('user32.dll');
if (u32) {
  var p = u32.findExportByName('CreateWindowExW');
  Interceptor.attach(p, { onEnter: function(a){
    try{
      var cls = a[1].readUtf16String();
      if (/ThunderRT6/.test(cls)) emit('CreateWindow cls=' + cls + ' title=' + JSON.stringify(a[2].isNull()?'':a[2].readUtf16String()) + ' style=' + hx(a[3].toUInt32()));
    }catch(e){}
  }});
}
emit('diag12 ready');
