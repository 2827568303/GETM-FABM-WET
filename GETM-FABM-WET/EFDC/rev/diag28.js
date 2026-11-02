'use strict';
// diag28.js — 对 licenseWrapper 的 IDispatch 做全量观测（名字 + DISPID + 调用）
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function hexg(p){ try{ var u=new Uint8Array(p.readByteArray(16)); return Array.from(u).map(function(x){return x.toString(16).padStart(2,'0');}).join(''); }catch(e){ return '?'; } }
function hx(v){ return ('00000000'+(v>>>0).toString(16)).slice(-8); }

var IID_IDISPATCH = [0x00,0x04,0x02,0x00,0x00,0x00,0x00,0x00,0xC0,0x00,0x00,0x00,0x00,0x00,0x00,0x46];
var hookedVt = {};

var ole = Process.findModuleByName('combase.dll') || Process.findModuleByName('ole32.dll');
var pCCI = ole.findExportByName('CoCreateInstanceEx');

Interceptor.attach(pCCI, {
  onEnter: function(a){
    this.pResults = a[5];
    this.clsid = hexg(a[0]);
  },
  onLeave: function(r){
    var mq;
    try { mq = this.pResults; } catch (e) { return; }
    if (!mq || mq.isNull()) return;
    var itf;
    try { itf = mq.add(4).readPointer(); } catch (e) { return; }
    if (itf.isNull()) return;

    var vt = itf.readPointer();
    var key = vt.toString();
    if (hookedVt[key]) return;
    hookedVt[key] = 1;
    emit('=== 接口 itf=' + itf + ' clsid=' + this.clsid);

    try {
      var qi = new NativeFunction(vt.readPointer(), 'uint', ['pointer', 'pointer', 'pointer']);
      var iidDisp = Memory.alloc(16); iidDisp.writeByteArray(new Uint8Array(IID_IDISPATCH));
      var ppv = Memory.alloc(4); ppv.writePointer(ptr(0));
      var hr = qi(itf, iidDisp, ppv);
      var disp = ppv.readPointer();
      emit('  QI(IDispatch) hr=0x' + hx(hr) + ' disp=' + disp);
      if (hr !== 0 || disp.isNull()) return;

      var dvt = disp.readPointer();
      var getIDs = dvt.add(5 * 4).readPointer();
      var invoke = dvt.add(6 * 4).readPointer();
      emit('  IDispatch vtable=' + dvt + ' GetIDsOfNames=' + getIDs + ' Invoke=' + invoke);

      Interceptor.attach(getIDs, { onEnter: function(a){
        try {
          var cnt = a[3].toInt32();
          var arr = a[2];
          var names = [];
          for (var i = 0; i < cnt; i++) {
            var sp = arr.add(i * 4).readPointer();
            names.push(sp.isNull() ? '<null>' : sp.readUtf16String());
          }
          emit('  GetIDsOfNames ' + JSON.stringify(names));
        } catch (e) { emit('  GIDN err ' + e); }
      }});

      Interceptor.attach(invoke, { onEnter: function(a){
        var flags = a[2].toInt32() >>> 0;
        var dispId = a[1].toInt32();
        var argc = a[3].toInt32();
        emit('  Invoke dispId=' + dispId + ' flags=0x' + flags.toString(16) + ' argc=' + argc);
        try {
          var vp = a[4]; // DISPPARAMS*
          if (vp && !vp.isNull()) {
            var rgvarg = vp.readPointer();
            var n = Math.min(argc, 4);
            for (var i = 0; i < n; i++) {
              var va = rgvarg.add(i * 16);
              var vt = va.readU16();
              var val = va.add(8).readPointer();
              var extra = '';
              if (vt === 8) { try { extra = ' str=' + JSON.stringify(val.readUtf16String()); } catch (e) {} }
              emit('     arg' + i + ' vt=' + vt + extra);
            }
          }
        } catch (e) { emit('     args err ' + e); }
      }});
    } catch (e) { emit('  hook err ' + e); }
  }
});
emit('diag28 ready');
