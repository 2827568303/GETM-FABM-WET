'use strict';
// picture shim + capture VB6 MsgBox through rtcMsgBox / DialogBox APIs
var t0 = Date.now();
function ts(){ return (Date.now()-t0).toString().padStart(6,' '); }
function emit(s){ send(ts()+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }
function bstr(p){ try{ if(p.isNull()) return '<null>'; return p.readUtf16String()||''; }catch(e){ return '<err>'; } }

var oa = Process.findModuleByName('oleaut32.dll');
var gdi = Process.findModuleByName('gdi32.dll');
var pLoadEx = oa.findExportByName('OleLoadPictureEx');
var OleCreate = new NativeFunction(oa.findExportByName('OleCreatePictureIndirect'), 'uint', ['pointer','pointer','int','pointer']);
var CreateCompatibleDC = new NativeFunction(gdi.findExportByName('CreateCompatibleDC'), 'pointer', ['pointer']);
var CreateCompatibleBitmap = new NativeFunction(gdi.findExportByName('CreateCompatibleBitmap'), 'pointer', ['pointer','int','int']);
var IID_IPicture = [0x80,0x09,0xF8,0x7B,0x32,0xBF,0x1A,0x10,0x8B,0xBB,0x00,0xAA,0x00,0x30,0x0C,0xAB];
Interceptor.attach(pLoadEx, {
  onEnter: function(a){ this.out = a[7]; },
  onLeave: function(r){
    if ((r.toInt32()>>>0) === 0) return;
    try{
      var hdc = CreateCompatibleDC(ptr(0));
      var hbmp = CreateCompatibleBitmap(hdc, 16, 16);
      var desc = Memory.alloc(24);
      desc.writeU32(24); desc.add(4).writeU32(1); desc.add(8).writePointer(hbmp);
      desc.add(0xc).writePointer(ptr(0)); desc.add(0x10).writePointer(ptr(0));
      var ppv = Memory.alloc(4);
      var iidP = Memory.alloc(16); iidP.writeByteArray(new Uint8Array(IID_IPicture));
      if ((OleCreate(desc, iidP, 1, ppv)>>>0) === 0) { this.out.writePointer(ppv.readPointer()); r.replace(ptr(0)); emit('pix substituted'); }
    }catch(e){ emit('pix err '+e); }
  }
});

var vb = Process.findModuleByName('MSVBVM60.DLL');
if (vb) {
  ['rtcMsgBox'].forEach(function(nm){
    try{ var f = vb.findExportByName(nm);
      if(f) Interceptor.attach(f, { onEnter: function(a){ emit(nm+'('+bstr(a[0])+') from '+mod(this.returnAddress)); } });
    }catch(e){ emit('hook '+nm+' err '+e); }
  });
}
var u32 = Process.findModuleByName('user32.dll');
[['DialogBoxParamW',1],['DialogBoxParamA',1],['DialogBoxIndirectParamW',1],['MessageBoxIndirectA',0]].forEach(function(pair){
  try{
    var nm = pair[0], f = u32.findExportByName(nm);
    if (f) Interceptor.attach(f, { onEnter: function(a){ emit(nm+' from '+mod(this.returnAddress)); } });
  }catch(e){ emit('hook '+nm+' err '+e); }
});
emit('ready v7');
