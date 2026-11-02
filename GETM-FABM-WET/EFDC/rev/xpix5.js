'use strict';
// MSVBVM60 (6.00.9848) calls OleLoadPictureEx with the OLD 8-param prototype:
//   (stream, size, xW, yH, xDpi, yDpi, flags, ppvObj)  <-- no riid
// so the object pointer must be written to a[7] (what Frida sees as "riid"),
// NOT a[8] (that slot is the wrapper's saved EBP -> corrupts the stack).
var t0 = Date.now();
function ts(){ return (Date.now()-t0).toString().padStart(6,' '); }
function emit(s){ send(ts()+' '+s); }

var oa = Process.findModuleByName('oleaut32.dll');
var gdi = Process.findModuleByName('gdi32.dll');
var pLoadEx = oa.findExportByName('OleLoadPictureEx');
var OleCreate = new NativeFunction(oa.findExportByName('OleCreatePictureIndirect'), 'uint', ['pointer','pointer','int','pointer']);
var CreateCompatibleDC = new NativeFunction(gdi.findExportByName('CreateCompatibleDC'), 'pointer', ['pointer']);
var CreateCompatibleBitmap = new NativeFunction(gdi.findExportByName('CreateCompatibleBitmap'), 'pointer', ['pointer','int','int']);
var IID_IPicture = [0x80,0x09,0xF8,0x7B,0x32,0xBF,0x1A,0x10,0x8B,0xBB,0x00,0xAA,0x00,0x30,0x0C,0xAB];

var n = 0, made = 0;
Interceptor.attach(pLoadEx, {
  onEnter: function(a){ this.out = a[7]; },
  onLeave: function(r){
    var hr = r.toInt32()>>>0;
    if (hr === 0) { n++; return; }
    try{
      var hdc = CreateCompatibleDC(ptr(0));
      var hbmp = CreateCompatibleBitmap(hdc, 16, 16);
      var desc = Memory.alloc(24);
      desc.writeU32(24); desc.add(4).writeU32(1); desc.add(8).writePointer(hbmp);
      desc.add(0xc).writePointer(ptr(0)); desc.add(0x10).writePointer(ptr(0));
      var ppv = Memory.alloc(4);
      var iidP = Memory.alloc(16); iidP.writeByteArray(new Uint8Array(IID_IPicture));
      var hr2 = OleCreate(desc, iidP, 1, ppv);
      if ((hr2>>>0) === 0) {
        this.out.writePointer(ppv.readPointer());
        r.replace(ptr(0));
        made++;
        emit('LoadEx#'+n+' real=0x'+hr.toString(16)+' -> substituted IPicture '+ppv.readPointer()+' into '+this.out);
      } else {
        emit('LoadEx#'+n+' OleCreate failed 0x'+(hr2>>>0).toString(16));
      }
    }catch(e){ emit('err '+e); }
    n++;
  }
});
emit('ready v5 (write out to a[7], old prototype)');
