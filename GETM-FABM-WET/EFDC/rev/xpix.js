'use strict';
// Correct picture shim: OleLoadPictureEx has 9 params; a[8] is the out pointer.
var t0 = Date.now();
function ts(){ return (Date.now()-t0).toString().padStart(6,' '); }
function emit(s){ send(ts()+' '+s); }

var oa = Process.findModuleByName('oleaut32.dll');
var gdi = Process.findModuleByName('gdi32.dll');
var pLoadEx = oa.findExportByName('OleLoadPictureEx');
var OleCreate = new NativeFunction(oa.findExportByName('OleCreatePictureIndirect'), 'uint', ['pointer','pointer','int','pointer']);
var CreateCompatibleDC = new NativeFunction(gdi.findExportByName('CreateCompatibleDC'), 'pointer', ['pointer']);
var CreateCompatibleBitmap = new NativeFunction(gdi.findExportByName('CreateCompatibleBitmap'), 'pointer', ['pointer','int','int']);
var GetDC = new NativeFunction(gdi.findExportByName('GetDC'), 'pointer', ['pointer']);

var n = 0;
Interceptor.attach(pLoadEx, {
  onEnter: function(a){
    this.out = a[8];
    this.riid = a[7];
    this.ret = this.returnAddress;
  },
  onLeave: function(r){
    var hr = r.toInt32() >>> 0;
    if (hr === 0) { emit('LoadEx#'+n+' ok'); n++; return; }
    try{
      var hdc = CreateCompatibleDC(ptr(0));
      var hbmp = CreateCompatibleBitmap(hdc, 16, 16);
      var desc = Memory.alloc(24);
      desc.writeU32(24);          // cbSizeOfStruct
      desc.add(4).writeU32(1);    // PICTYPE_BITMAP
      desc.add(8).writePointer(hbmp);
      desc.add(0xc).writePointer(ptr(0));
      desc.add(0x10).writePointer(ptr(0));
      var ppv = Memory.alloc(4);
      var riid = this.riid.readByteArray(16);
      var buf = Memory.alloc(16); buf.writeByteArray(riid);
      var hr2 = OleCreate(desc, buf, 1, ppv);
      emit('LoadEx#'+n+' was 0x'+hr.toString(16)+' -> substitute OleCreatePictureIndirect hr=0x'+(hr2>>>0).toString(16)+' obj='+ppv.readPointer());
      if ((hr2>>>0) === 0) {
        this.out.writePointer(ppv.readPointer());
        r.replace(ptr(0));
      }
    }catch(e){ emit('subst err '+e); }
    n++;
  }
});
emit('ready (correct picfix, out=a[8])');
