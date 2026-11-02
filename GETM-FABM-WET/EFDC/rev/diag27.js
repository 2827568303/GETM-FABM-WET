'use strict';
// diag27.js — 挂到 licenseWrapper 的 IDispatch 上，看 VB6 到底问了什么
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function hexg(p){ try{ var u=new Uint8Array(p.readByteArray(16)); return Array.from(u).map(function(x){return x.toString(16).padStart(2,'0');}).join(''); }catch(e){ return '?'; } }

var ole = Process.findModuleByName('combase.dll') || Process.findModuleByName('ole32.dll');
var p = ole.findExportByName('CoCreateInstanceEx');
var hooked = {};

Interceptor.attach(p, {
  onLeave: function(r){
    var hr = r.toInt32() >>> 0;
    if (hr !== 0) return;
    var mq = this.pResults;
    if (!mq || mq.isNull()) return;
    var itf = mq.add(4).readPointer();
    if (itf.isNull()) return;
    var vt;
    try { vt = itf.readPointer(); } catch (e) { return; }
    var key = vt.toString();
    if (hooked[key]) return;
    hooked[key] = 1;
    emit('发现接口 itf=' + itf + ' vtable=' + vt + ' (clsid=' + this.clsid + ')');
    try {
      var qi = vt.readPointer();
      var addref = vt.add(4).readPointer();
      var release = vt.add(8).readPointer();
      var getTypeInfoCount = vt.add(12).readPointer();
      var getTypeInfo = vt.add(16).readPointer();
      var getIDs = vt.add(20).readPointer();
      var invoke = vt.add(24).readPointer();
      emit('  vt: qi=' + qi + ' gidn=' + getIDs + ' invoke=' + invoke);
      Interceptor.attach(getIDs, { onEnter: function(a){
        try{
          var names = [];
          var arr = a[2];
          for (var i = 0; i < a[3].toInt32(); i++) {
            var s = arr.add(i * 4).readPointer();
            names.push(s.isNull() ? '<null>' : s.readUtf16String());
          }
          emit('  GetIDsOfNames: ' + JSON.stringify(names));
        }catch(e){ emit('  GetIDsOfNames err ' + e); }
      }});
      Interceptor.attach(invoke, { onEnter: function(a){
        emit('  Invoke dispId=' + a[1].toInt32() + ' flags=0x' + (a[2].toInt32() >>> 0).toString(16));
        try{
          if ((a[2].toInt32() & 4) === 0 && a[3].toInt32() === 1) {
            var v = a[5];
            emit('    arg varType=' + v.readU16());
          }
        }catch(e){}
      }});
    } catch (e) { emit('  hook err ' + e); }
  }
});
emit('diag27 ready');
