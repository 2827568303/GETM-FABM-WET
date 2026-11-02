'use strict';
// diag51.js — 让 OleLoadPictureEx 成功（返回一张真实的小位图 IPicture）
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }

var oa = Process.findModuleByName('oleaut32.dll');
var gdi = Process.findModuleByName('gdi32.dll');

var OleCreatePictureIndirect = new NativeFunction(oa.findExportByName('OleCreatePictureIndirect'), 'uint', ['pointer', 'pointer', 'int', 'pointer']);
var CreateCompatibleDC = new NativeFunction(gdi.findExportByName('CreateCompatibleDC'), 'pointer', ['pointer']);
var CreateCompatibleBitmap = new NativeFunction(gdi.findExportByName('CreateCompatibleBitmap'), 'pointer', ['pointer', 'int', 'int']);

var made = 0;

Interceptor.attach(oa.findExportByName('OleLoadPictureEx'), {
  onEnter: function(a){
    this.ppv = a[7];
    this.riid = a[3];
    this.size = a[1].toInt32();
  },
  onLeave: function(r){
    var hr = r.toInt32() >>> 0;
    if (hr === 0) return;
    try {
      var hdc = CreateCompatibleDC(ptr(0));
      var hbm = CreateCompatibleBitmap(hdc, 16, 16);
      var desc = Memory.alloc(16);
      desc.writeU32(16);          // cbSize
      desc.writeU32(1);           // PICTYPE_BITMAP(1)
      desc.add(8).writePointer(hbm);
      desc.add(12).writePointer(ptr(0));
      var hr2 = OleCreatePictureIndirect(desc, this.riid, 1, this.ppv);
      emit('SUBSTITUTE hr_orig=0x' + hr.toString(16) + ' -> create=0x' + (hr2 >>> 0).toString(16) + ' ppv=' + this.ppv);
      if ((hr2 >>> 0) === 0) r.replace(ptr(0));
    } catch (e) { emit('substitute err ' + e); }
  }
});

var u32 = Process.findModuleByName('user32.dll');
Interceptor.attach(u32.findExportByName('SoftModalMessageBox'), { onEnter: function(){ emit('=== MSGBOX ==='); }});
emit('diag51 ready');
