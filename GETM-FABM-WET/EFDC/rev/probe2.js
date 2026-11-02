'use strict';
// probe2.js — pic shim + msgbox text + flow trace + m2b0 slot resolve
var t0 = Date.now();
function ts(){ return (Date.now()-t0).toString().padStart(6,' '); }
function emit(s){ send(ts()+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(ptr(a)); return m?(m.name+'+0x'+ptr(a).sub(m.base).toString(16)):(ptr(a).toString()); }catch(e){ return '?'; } }
function bstr(p){ try{ if(p.isNull()) return '<null>'; return p.readUtf16String()||''; }catch(e){ return '<err>'; } }

// ---------- picture shim ----------
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
      if ((OleCreate(desc, iidP, 1, ppv)>>>0) === 0) {
        this.out.writePointer(ppv.readPointer()); r.replace(ptr(0));
        emit('pix substituted');
      }
    }catch(e){ emit('pix err '+e); }
  }
});

// ---------- flow ----------
function hookFlow(addr, name){
  Interceptor.attach(ptr(addr), {
    onEnter: function(){ emit('ENTER '+name); },
    onLeave: function(r){ emit('LEAVE '+name+' ret='+r.toInt32()); }
  });
}
hookFlow(0x81C4C0, 'CheckLicensing');
hookFlow(0x828F50, 'SplashInit');
hookFlow(0x156ACC0, 'TitleInit');
hookFlow(0x156AD74, 'M250');

// ---------- m2b0 ----------
var slotTarget = null;
Interceptor.attach(ptr(0x156AE23), {
  onEnter: function(){
    var edi = this.context.edi;
    var target = edi.add(0x2B0).readPointer();
    emit('M2B0 edi='+edi+' slot0x2B0='+target+' -> '+mod(target));
    slotTarget = target;
    try{
      var esp = this.context.esp;
      var words=[];
      for(var o=0;o<0x60;o+=4){ words.push('+'+o.toString(16)+':'+esp.add(o).readU32().toString(16)); }
      emit('STACK '+words.join(' '));
    }catch(e){}
    if(!this.hooked){
      this.hooked=1;
      try{
        Interceptor.attach(target, {
          onEnter: function(){ this.t=Date.now(); emit('THUNK ENTER '+mod(target)); },
          onLeave: function(r){ emit('THUNK LEAVE after '+((Date.now()-this.t)/1000).toFixed(2)+'s'); }
        });
      }catch(e){ emit('thunk hook err '+e); }
    }
  }
});

// ---------- message boxes with text ----------
try{
  var vb = Process.findModuleByName('MSVBVM60.DLL');
  Interceptor.attach(vb.findExportByName('rtcMsgBox'), {
    onEnter: function(a){ emit('rtcMsgBox TEXT='+JSON.stringify(bstr(a[0]))+' from '+mod(this.returnAddress)); }
  });
}catch(e){ emit('rtc hook err '+e); }
try{
  var u32 = Process.findModuleByName('user32.dll');
  Interceptor.attach(u32.findExportByName('MessageBoxW'), {
    onEnter: function(a){ emit('MsgBoxW TEXT='+JSON.stringify(bstr(a[1]))+' CAP='+JSON.stringify(bstr(a[2]))+' from '+mod(this.returnAddress)); }
  });
  Interceptor.attach(u32.findExportByName('MessageBoxA'), {
    onEnter: function(a){ emit('MsgBoxA TEXT='+JSON.stringify(a[1].readUtf8String())+' from '+mod(this.returnAddress)); }
  });
}catch(e){ emit('msgbox hook err '+e); }

// ---------- wait/network ----------
function hookExp(modname, name){
  try{
    var m = Process.findModuleByName(modname); if(!m) return;
    var f = m.findExportByName(name); if(!f) return;
    Interceptor.attach(f, { onEnter: function(){ emit(name+' from '+mod(this.returnAddress)); }});
  }catch(e){}
}
hookExp('kernelbase.dll','SleepEx');
hookExp('ws2_32.dll','connect');
hookExp('ws2_32.dll','send');
hookExp('ws2_32.dll','recv');
hookExp('winhttp.dll','WinHttpSendRequest');
hookExp('winhttp.dll','WinHttpReceiveResponse');
hookExp('wininet.dll','InternetOpenUrlW');

emit('probe2 ready');
