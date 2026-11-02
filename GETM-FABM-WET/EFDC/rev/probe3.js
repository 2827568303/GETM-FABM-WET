'use strict';
// probe3.js — find the raise site of VB6 Error 380
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
  onEnter: function(a){ this.out = a[7]; this.ret = this.returnAddress; },
  onLeave: function(r){
    if ((r.toInt32()>>>0) === 0) { emit('LoadEx OK from '+mod(this.ret)); return; }
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
        emit('LoadEx FAIL(0x'+ (r.toInt32()>>>0).toString(16) +') -> substituted, caller '+mod(this.ret));
      }
    }catch(e){ emit('pix err '+e); }
  }
});

// ---------- RaiseException hook: VB6 runtime errors arrive as SEH ----------
function stackScan(ctx, depth){
  var out=[];
  try{
    var esp = ctx.esp;
    for(var o=0;o<0x200;o+=4){
      var v = esp.add(o).readU32();
      var s = mod(v);
      if(s && (s.indexOf('EFDC')===0 || s.indexOf('MSVBVM')===0)) out.push('+'+o.toString(16)+' '+s);
    }
  }catch(e){}
  return out.slice(0,18).join(' | ');
}
try{
  var kb = Process.findModuleByName('kernelbase.dll');
  var re = kb.findExportByName('RaiseException');
  Interceptor.attach(re, {
    onEnter: function(a){
      var code = a[0].toInt32()>>>0;
      var s = stackScan(this.context);
      emit('RaiseException code=0x'+code.toString(16)+' flags='+a[1]+' ret='+mod(this.returnAddress)+' STACK: '+s);
    }
  });
}catch(e){ emit('RaiseException hook err '+e); }
try{
  var nt = Process.findModuleByName('ntdll.dll');
  Interceptor.attach(nt.findExportByName('RtlRaiseException'), {
    onEnter: function(a){
      var code = a[0].add(0).readU32();
      var s = stackScan(this.context);
      emit('RtlRaiseException code=0x'+code.toString(16)+' ret='+mod(this.returnAddress)+' STACK: '+s);
    }
  });
}catch(e){ emit('RtlRaiseException hook err '+e); }

// ---------- msgbox text ----------
try{
  var vb = Process.findModuleByName('MSVBVM60.DLL');
  Interceptor.attach(vb.findExportByName('rtcMsgBox'), {
    onEnter: function(a){ emit('rtcMsgBox TEXT='+JSON.stringify(bstr(a[0]))+' from '+mod(this.returnAddress)); }
  });
}catch(e){}

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

emit('probe3 ready');
