'use strict';
var t0 = Date.now();
function ts(){ return (Date.now()-t0).toString().padStart(6,' '); }
function emit(s){ send(ts()+' '+s); }
function hexbuf(p, n){ var out=[]; for (var i=0;i<n;i++){ try{ out.push(('0'+p.add(i).readU8().toString(16)).slice(-2)); }catch(e){ break; } } return out.join(' '); }

var oa = Process.findModuleByName('oleaut32.dll');
var gdi = Process.findModuleByName('gdi32.dll');
var pLoadEx = oa.findExportByName('OleLoadPictureEx');
var OleCreate = new NativeFunction(oa.findExportByName('OleCreatePictureIndirect'), 'uint', ['pointer','pointer','int','pointer']);
var CreateCompatibleDC = new NativeFunction(gdi.findExportByName('CreateCompatibleDC'), 'pointer', ['pointer']);
var CreateCompatibleBitmap = new NativeFunction(gdi.findExportByName('CreateCompatibleBitmap'), 'pointer', ['pointer','int','int']);
var IID_IPicture = [0x80,0x09,0xF8,0x7B,0x32,0xBF,0x1A,0x10,0x8B,0xBB,0x00,0xAA,0x00,0x30,0x0C,0xAB];

var n = 0;
Interceptor.attach(pLoadEx, {
  onEnter: function(a){
    this.out = a[8];
    this.riid = a[7];
    this.riidHex = hexbuf(a[7], 16);
  },
  onLeave: function(r){
    var hr = r.toInt32() >>> 0;
    emit('LoadEx#'+n+' hr=0x'+hr.toString(16)+' riid='+this.riidHex+' out='+this.out);
    if (hr === 0) { n++; return; }
    try{
      var hdc = CreateCompatibleDC(ptr(0));
      var hbmp = CreateCompatibleBitmap(hdc, 16, 16);
      emit('   hdc='+hdc+' hbmp='+hbmp);
      var desc = Memory.alloc(24);
      desc.writeU32(24);
      desc.add(4).writeU32(1);
      desc.add(8).writePointer(hbmp);
      desc.add(0xc).writePointer(ptr(0));
      desc.add(0x10).writePointer(ptr(0));
      var ppv = Memory.alloc(4);
      var iidP = Memory.alloc(16); iidP.writeByteArray(new Uint8Array(IID_IPicture));
      var hr2 = OleCreate(desc, iidP, 1, ppv);
      emit('   OleCreatePictureIndirect(IID_IPicture) hr=0x'+(hr2>>>0).toString(16)+' obj='+ppv.readPointer());
      if ((hr2>>>0) === 0) {
        var pic = ppv.readPointer();
        var p2 = Memory.alloc(4);
        var vt = pic.readPointer();
        var QI = new NativeFunction(vt.readPointer(), 'uint', ['pointer','pointer','pointer']);
        var hr3 = QI(pic, this.riid, p2);
        emit('   QI(caller riid) hr=0x'+(hr3>>>0).toString(16)+' obj='+p2.readPointer());
        this.out.writePointer(((hr3>>>0)===0) ? p2.readPointer() : pic);
        r.replace(ptr(0));
      }
    }catch(e){ emit('   subst err '+e); }
    n++;
  }
});
emit('ready v3');
