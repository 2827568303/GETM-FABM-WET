'use strict';
// diag24.js — 检查 CoCreateInstanceEx 的 IID 与 HRESULT（判断 licenseWrapper 为什么"not valid"）
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function hexg(p){ try{ var u=new Uint8Array(p.readByteArray(16)); return Array.from(u).map(function(x){return x.toString(16).padStart(2,'0');}).join(''); }catch(e){ return '?'; } }
function gs(hexs){
  if(!hexs || hexs==='?' || hexs.length!==32) return hexs;
  var b=hexs;
  return '{'+b.slice(6,8)+b.slice(4,6)+b.slice(2,4)+b.slice(0,2)+'-'+b.slice(10,12)+b.slice(8,10)+'-'+b.slice(14,16)+b.slice(12,14)+'-'+b.slice(16,20)+'-'+b.slice(20)  +'}';
}

var ole = Process.findModuleByName('combase.dll') || Process.findModuleByName('ole32.dll');
var p = ole.findExportByName('CoCreateInstanceEx');
Interceptor.attach(p, {
  onEnter: function(a){
    this.clsid = hexg(a[0]);
    this.riid = hexg(a[1]);
    this.pResults = a[5]; this.cmq = a[4].toInt32();
  },
  onLeave: function(r){
    var hr = r.toInt32() >>> 0;
    if (hr !== 0 || /6399e2c8|e326a913/i.test(this.clsid)) {
      emit('CoCreateInstanceEx clsid=' + this.clsid + ' riid=' + this.riid + ' hr=0x' + hr.toString(16));
      try {
        // MULTI_QI: {pIID, pItf, hr}
        var mq = this.pResults;
        if (mq && !mq.isNull()) {
          var iidp = mq.readPointer();
          emit('   -> cmq=' + this.cmq + ' iid=' + (iidp.isNull() ? '<?>' : hexg(iidp)));
          var itf = mq.add(4).readPointer();
          var hr2 = mq.add(8).readU32() >>> 0;
          emit('   -> pItf=' + itf + ' qi.hr=0x' + hr2.toString(16));
        }
      } catch (e) {}
    }
  }
});
emit('diag24 ready');

