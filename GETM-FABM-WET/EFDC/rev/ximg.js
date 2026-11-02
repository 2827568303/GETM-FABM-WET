'use strict';
var t0 = Date.now();
function ts(){ return (Date.now()-t0).toString().padStart(6,' '); }
function emit(s){ send(ts()+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }

var oa = Process.findModuleByName('oleaut32.dll');
var pLoadEx = oa.findExportByName('OleLoadPictureEx');
var pLoad   = oa.findExportByName('OleLoadPicture');
var Load = new NativeFunction(pLoad, 'uint', ['pointer','int','int','pointer','pointer']);

var IID_IPicture = [0x80,0x09,0xF8,0x7B,0x32,0xBF,0x1A,0x10,0x8B,0xBB,0x00,0xAA,0x00,0x30,0x0C,0xAB];
var IID_IPictureDisp = [0x81,0x09,0xF8,0x7B,0x32,0xBF,0x1A,0x10,0x8B,0xBB,0x00,0xAA,0x00,0x30,0x0C,0xAB];

var n = 0;
Interceptor.attach(pLoadEx, {
  onEnter: function(a){
    this.ret = this.returnAddress;
    var size = a[1].toInt32();
    this.size = size;
    try{
      var bytes = a[0].readByteArray(size);
      var u8 = new Uint8Array(bytes);
      var head = [];
      for (var i=0;i<Math.min(16,u8.length);i++) head.push(('0'+u8[i].toString(16)).slice(-2));
      emit('OleLoadPictureEx size='+size+' hdr='+head.join(' ')+' from '+mod(this.ret));
      if (u8.length > 0x20){
        var f = new File('/tmp/img_'+n+'.bin', 'wb');
        f.write(bytes); f.flush(); f.close();
      } else {
        var f2 = new File('/tmp/img_'+n+'.bin', 'wb');
        f2.write(bytes); f2.flush(); f2.close();
      }
    }catch(e){ emit('  dump err '+e); }
    this.ppv = a[6];
    this.ppv8 = a[7];
    n++;
  },
  onLeave: function(r){
    var hr = r.toInt32()>>>0;
    emit('  -> hr=0x'+hr.toString(16));
    if (hr !== 0) {
      // try the classic entry point with the correct 5-arg signature
      try{
        var iid = Memory.alloc(24);
        iid.writeByteArray(new Uint8Array(IID_IPicture));
        var out = Memory.alloc(4);
        var hr2 = Load(this.streamOrDefault ? this.streamOrDefault : ptr(0), this.size, 0, iid, out);
        emit('  retry OleLoadPicture -> 0x'+(hr2>>>0).toString(16));
      }catch(e){ emit('  retry err '+e); }
    }
  }
});
// also log direct OleLoadPicture calls
Interceptor.attach(pLoad, {
  onEnter: function(a){ this.ret = this.returnAddress; emit('OleLoadPicture size='+a[1].toInt32()+' from '+mod(this.ret)); },
  onLeave: function(r){ emit('  -> hr=0x'+((r.toInt32()>>>0)).toString(16)); }
});
emit('ready');
