'use strict';
// picture shim (write out to a[7], old 8-arg prototype) + MsgBox text capture
var t0 = Date.now();
function ts(){ return (Date.now()-t0).toString().padStart(6,' '); }
function emit(s){ send(ts()+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }
function wstr(p){ try{ return p.readUtf16String()||''; }catch(e){ return ''; } }

var oa = Process.findModuleByName('oleaut32.dll');
var gdi = Process.findModuleByName('gdi32.dll');
var pLoadEx = oa.findExportByName('OleLoadPictureEx');
var OleCreate = new NativeFunction(oa.findExportByName('OleCreatePictureIndirect'), 'uint', ['pointer','pointer','int','pointer']);
var CreateCompatibleDC = new NativeFunction(gdi.findExportByName('CreateCompatibleDC'), 'pointer', ['pointer']);
var CreateCompatibleBitmap = new NativeFunction(gdi.findExportByName('CreateCompatibleBitmap'), 'pointer', ['pointer','int','int']);
var IID_IPicture = [0x80,0x09,0xF8,0x7B,0x32,0xBF,0x1A,0x10,0x8B,0xBB,0x00,0xAA,0x00,0x30,0x0C,0xAB];
var n = 0;
Interceptor.attach(pLoadEx, {
  onEnter: function(a){ this.out = a[7]; },
  onLeave: function(r){
    if ((r.toInt32()>>>0) === 0) { n++; return; }
    try{
      var hdc = CreateCompatibleDC(ptr(0));
      var hbmp = CreateCompatibleBitmap(hdc, 16, 16);
      var desc = Memory.alloc(24);
      desc.writeU32(24); desc.add(4).writeU32(1); desc.add(8).writePointer(hbmp);
      desc.add(0xc).writePointer(ptr(0)); desc.add(0x10).writePointer(ptr(0));
      var ppv = Memory.alloc(4);
      var iidP = Memory.alloc(16); iidP.writeByteArray(new Uint8Array(IID_IPicture));
      if ((OleCreate(desc, iidP, 1, ppv)>>>0) === 0) {
        this.out.writePointer(ppv.readPointer());
        r.replace(ptr(0));
        emit('LoadEx#'+n+' substituted');
      }
    }catch(e){ emit('pix err '+e); }
    n++;
  }
});

var u32 = Process.findModuleByName('user32.dll');
try{
  Interceptor.attach(u32.findExportByName('MessageBoxW'), {
    onEnter: function(a){ emit('MessageBoxW hwnd='+a[0]+' text='+JSON.stringify(wstr(a[1]))+' caption='+JSON.stringify(wstr(a[2]))+' from '+mod(this.returnAddress)); }
  });
}catch(e){ emit('mb1 '+e); }
try{
  Interceptor.attach(u32.findExportByName('MessageBoxIndirectW'), {
    onEnter: function(p){
      var mp = p[0];
      var text = wstr(mp.add(8 + 4 + 4).readPointer());   // MSGBOXPARAMSW: cbSize, hwndOwner, hInstance, lpszText
      emit('MessageBoxIndirectW raw='+mp+' from '+mod(this.returnAddress));
      try{
        emit('   cbSize='+mp.readU32()+' hwnd='+mp.add(4).readPointer()+' hInst='+mp.add(8).readPointer()+' text='+JSON.stringify(wstr(mp.add(12).readPointer()))+' caption='+JSON.stringify(wstr(mp.add(16).readPointer())));
      }catch(e){ emit('   parse err '+e); }
    }
  });
}catch(e){ emit('mb2 '+e); }
try{
  Interceptor.attach(u32.findExportByName('MessageBoxA'), {
    onEnter: function(a){ var s=''; try{ s=a[1].readAnsiString()||''; }catch(e){} emit('MessageBoxA text='+JSON.stringify(s)+' from '+mod(this.returnAddress)); }
  });
}catch(e){ emit('mb3 '+e); }
emit('ready v6');
