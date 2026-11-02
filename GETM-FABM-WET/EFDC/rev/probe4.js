'use strict';
// probe4.js — EBP-chain backtrace at the VB6 error raiser & picture substitution
var t0 = Date.now();
function ts(){ return (Date.now()-t0).toString().padStart(6,' '); }
function emit(s){ send(ts()+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(ptr(a)); return m?(m.name+'+0x'+ptr(a).sub(m.base).toString(16)):(ptr(a).toString()); }catch(e){ return '?'; } }
function bstr(p){ try{ if(p.isNull()) return '<null>'; return p.readUtf16String()||''; }catch(e){ return '<err>'; } }

function walkChain(ebp, maxFrames){
  var out=[];
  var p = ptr(ebp); var guard=0;
  while(!p.isNull() && guard++ < maxFrames){
    var ret;
    try{ ret = p.add(4).readPointer(); }catch(e){ break; }
    out.push(mod(ret));
    var nxt;
    try{ nxt = p.readPointer(); }catch(e){ break; }
    if(nxt.isNull() || nxt.compare(p) <= 0 || nxt.sub(p).toInt32() > 0x200000) break;
    p = nxt;
  }
  return out.join(' | ');
}

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
        emit('PIX-SUB caller='+mod(this.returnAddress)+' CHAIN: '+walkChain(this.context.ebp, 16));
      }
    }catch(e){ emit('pix err '+e); }
  }
});

// ---------- VB6 error raiser (calls RaiseException 0xc000008f) ----------
var vb = Process.findModuleByName('MSVBVM60.DLL');
var raiser = vb.base.add(0x384a7);
Interceptor.attach(raiser, {
  onEnter: function(a){
    var ctx = this.context;
    var vals = [];
    for(var o=4;o<0x28;o+=4){ try{ vals.push('['+o.toString(16)+']='+ctx.esp.add(o).readU32().toString(16)); }catch(e){ break; } }
    emit('RAISER ret='+mod(this.returnAddress)+' '+vals.join(' '));
    emit('RAISER CHAIN: '+walkChain(ctx.ebp, 16));
  }
});

// ---------- msgbox ----------
try{
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

emit('probe4 ready raiser='+raiser);
