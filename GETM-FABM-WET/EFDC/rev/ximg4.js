'use strict';
var t0 = Date.now();
function ts(){ return (Date.now()-t0).toString().padStart(6,' '); }
function emit(s){ send(ts()+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }
var OUT = 'C:\\Users\\23801\\Desktop\\GETM-FABM-WET-260928\\GETM-FABM-WET\\EFDC\\rev\\stream';

var oa = Process.findModuleByName('oleaut32.dll');
var pLoadEx = oa.findExportByName('OleLoadPictureEx');
var n = 0;

function fnAt(obj, idx){ var v = obj.readPointer(); return v.add(idx*4).readPointer(); }

Interceptor.attach(pLoadEx, {
  onEnter: function(a){
    this.ret = this.returnAddress;
    var stream = a[0], size = a[1].toInt32();
    emit('LoadEx#'+n+' stream='+stream+' lSize='+size+' xW='+a[2]+' yH='+a[3]+' xDpi='+a[4]+' yDpi='+a[5]+' flags='+a[6]+' riid='+a[7]+' ppv='+a[8]+' from '+mod(this.ret));
    try{
      var stg = Memory.alloc(128);
      var Stat = new NativeFunction(fnAt(stream, 12), 'uint', ['pointer','pointer','uint']);
      var hr = Stat(stream, stg, 1);
      var cbSize = stg.add(8).readU64();
      var typ = stg.add(4).readU32();
      emit('   Stat hr=0x'+(hr>>>0).toString(16)+' cbSize='+cbSize+' type='+typ);
      var len = Number(cbSize);
      if (!(len > 0 && len <= 4*1024*1024)) len = size;
      if (!(len > 0 && len <= 4*1024*1024)) len = 4096;
      var buf = Memory.alloc(len);
      var pcb = Memory.alloc(4);
      var Read = new NativeFunction(fnAt(stream, 3), 'uint', ['pointer','pointer','uint','pointer']);
      var hr2 = Read(stream, buf, len, pcb);
      var got = pcb.readU32();
      emit('   Read hr=0x'+(hr2>>>0).toString(16)+' got='+got);
      var head = [];
      for (var i=0;i<Math.min(16,got);i++) head.push(('0'+buf.add(i).readU8().toString(16)).slice(-2));
      emit('   head='+head.join(' '));
      var f = new File(OUT+'_'+n+'.bin','wb');
      f.write(buf.readByteArray(got)); f.flush(); f.close();
    }catch(e){ emit('   dump err '+e); }
    n++;
  },
  onLeave: function(r){ emit('  -> hr=0x'+((r.toInt32()>>>0)).toString(16)); }
});
emit('ready');
