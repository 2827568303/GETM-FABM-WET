'use strict';
// diag41.js — 枚举窗体 vtable 槽位，记录启动期实际被调用的方法 ID
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function hx(v){ return ('00000000'+(v>>>0).toString(16)).slice(-8); }

var vb = Process.findModuleByName('MSVBVM60.DLL');
var pNew2 = vb.findExportByName('__vbaNew2');
var hookedVt = {};

function hookVtable(vt, tag){
  var key = vt.toString();
  if (hookedVt[key]) return;
  hookedVt[key] = 1;
  emit('hook vtable ' + vt + ' (' + tag + ')');
  for (var off = 0; off <= 0x400; off += 4) {
    (function(o){
      var p;
      try { p = vt.add(o).readPointer(); } catch (e) { return; }
      if (p.isNull()) return;
      try {
        Interceptor.attach(p, { onEnter: function(){ emit('  call slot 0x' + o.toString(16) + ' (id 0x' + (o/4).toString(16) + ')'); } });
      } catch (e) {}
    })(off);
  }
}

Interceptor.attach(pNew2, {
  onLeave: function(){
    try {
      var out = this.outPtr;
    } catch (e) {}
  },
  onEnter: function(a){
    this.out = a[1];
    this.ci = a[0];
  }
});

// 改为在 helper 里直接读全局对象
Interceptor.attach(ptr(0x156ABA0), { onEnter: function(){
  var obj = ptr(0x16249B0).readPointer();
  if (!obj.isNull()) {
    emit('form obj=' + obj + ' classinfo=' + hx(ptr(0x16249B0).readU32()));
    try { hookVtable(obj.readPointer(), 'form'); } catch (e) { emit('vtable hook err ' + e); }
  }
}});
emit('diag41 ready');
