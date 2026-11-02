'use strict';
// diag71.js — 记录所有窗体对象的方法槽调用（找出"显示窗体"用的槽）
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function hx(v){ return ('00000000'+(v>>>0).toString(16)).slice(-8); }

var vb = Process.findModuleByName('MSVBVM60.DLL');
var hooked = {};

Interceptor.attach(vb.findExportByName('__vbaNew2'), {
  onEnter: function(a){ this.out = a[1]; this.ci = a[0]; },
  onLeave: function(){
    var ci = 0, obj = null;
    try { ci = this.ci.toInt32() >>> 0; } catch (e) { return; }
    try { obj = this.out.readPointer(); } catch (e) { return; }
    if (!obj || obj.isNull()) return;
    var vt;
    try { vt = obj.readPointer(); } catch (e) { return; }
    var key = vt.toString();
    if (hooked[key]) { emit('new obj ci=' + hx(ci) + ' (vtable already hooked)'); return; }
    hooked[key] = 1;
    emit('hook vtable ' + vt + ' for ci=' + hx(ci) + ' obj=' + obj);
    for (var off = 0; off <= 0x400; off += 4) {
      (function(o){
        var p;
        try { p = vt.add(o).readPointer(); } catch (e) { return; }
        if (p.isNull()) return;
        try {
          Interceptor.attach(p, { onEnter: function(){
            emit('   call slot 0x' + o.toString(16) + ' (ci=' + hx(ci) + ')');
          }});
        } catch (e) {}
      })(off);
    }
  }
});
emit('diag71 ready');
