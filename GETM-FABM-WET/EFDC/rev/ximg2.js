'use strict';
var t0 = Date.now();
function ts(){ return (Date.now()-t0).toString().padStart(6,' '); }
function emit(s){ send(ts()+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }
var OUT = 'C:\\Users\\23801\\Desktop\\GETM-FABM-WET-260928\\GETM-FABM-WET\\EFDC\\rev\\img';

var oa = Process.findModuleByName('oleaut32.dll');
var pLoadEx = oa.findExportByName('OleLoadPictureEx');
var pLoad   = oa.findExportByName('OleLoadPicture');
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
      for (var i=0;i<Math.min(12,u8.length);i++) head.push(('0'+u8[i].toString(16)).slice(-2));
      emit('LoadEx#'+n+' size='+size+' hdr='+head.join(' ')+' from '+mod(this.ret));
      var f = new File(OUT+'_'+n+'.bin','wb'); f.write(bytes); f.flush(); f.close();
    }catch(e){ emit('  dump err '+e); }
    n++;
  },
  onLeave: function(r){ emit('  -> hr=0x'+((r.toInt32()>>>0)).toString(16)); }
});
Interceptor.attach(pLoad, {
  onEnter: function(a){ this.ret=this.returnAddress; emit('Load size='+a[1].toInt32()+' from '+mod(this.ret)); },
  onLeave: function(r){ emit('  -> hr=0x'+((r.toInt32()>>>0)).toString(16)); }
});
emit('ready');
