// Focus on the picture-loading path (OleLoadPictureEx & friends) + GDI+ decode results.
function hook(name, mod) {
  var a = null;
  try { a = Module.findGlobalExportByName(name); } catch (e) {}
  if (!a) { try { a = Module.findExportByName(mod || null, name); } catch (e) {} }
  if (!a) { send({ note: 'missing ' + name }); return; }
  Interceptor.attach(a, {
    onEnter: function (args) { this.a = Array.prototype.slice.call(args); },
    onLeave: function (ret) {
      var hr = ret.toInt32() >>> 0;
      send({ f: name, hr: '0x' + hr.toString(16) });
    }
  });
}
hook('OleLoadPictureEx', 'oleaut32.dll');
hook('OleLoadPicture', 'oleaut32.dll');
hook('OleLoadPicturePath', 'oleaut32.dll');
hook('OleCreatePictureIndirect', 'oleaut32.dll');
hook('OleTranslateColor', 'oleaut32.dll');
hook('CreateStreamOnHGlobal', 'ole32.dll');
hook('GetObjectW', 'gdi32.dll');
hook('LoadImageW', 'user32.dll');
hook('GdipCreateBitmapFromStream', 'gdiplus.dll');
hook('GdipLoadImageFromStream', 'gdiplus.dll');
hook('GdipCreateHBITMAPFromBitmap', 'gdiplus.dll');

// Resource-level: who calls FindResource for a BITMAP and does it succeed?
var fr = Module.findGlobalExportByName('FindResourceW');
if (fr) Interceptor.attach(fr, {
  onEnter: function (a) {
    var name = a[1];
    var s = null;
    try { s = name.toInt32() <= 0xffff ? '#' + name.toInt32() : name.readUtf16String(); } catch (e) {}
    this.name = s;
  },
  onLeave: function (r) { send({ res: this.name, ok: !r.isNull() }); }
});
