'use strict';
// probe_m2b0.js — trace TitleInit hang inside slot 0x2B0 dispatch
var t0 = Date.now();
function ts(){ return (Date.now()-t0).toString().padStart(6,' '); }
function emit(s){ send(ts()+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(ptr(a)); return m?(m.name+'+0x'+ptr(a).sub(m.base).toString(16)):(ptr(a).toString()); }catch(e){ return '?'; } }
function modOff(a){ try{ var m=Process.findModuleByAddress(ptr(a)); return m?(m.name+'+0x'+ptr(a).sub(m.base).toString(16)):null; }catch(e){ return null; } }

var EXE_BASE = ptr(0x400000);
var exeMod = Process.findModuleByName('EFDC_Explorer8.4.exe') || Process.getModuleByName('EFDC_Explorer8.4.exe');

// ---------- picture shim (prevent 481 dialog) ----------
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
        emit('pix substituted @'+this.out);
      }
    }catch(e){ emit('pix err '+e); }
  }
});

// ---------- flow hooks ----------
function hookFlow(addr, name){
  Interceptor.attach(ptr(addr), {
    onEnter: function(){ emit('ENTER '+name); },
    onLeave: function(r){ emit('LEAVE '+name+' ret='+r.toInt32()); }
  });
}
hookFlow(0x81C4C0, 'CheckLicensing');
hookFlow(0x828F50, 'SplashInit');
hookFlow(0x156ACC0, 'TitleInit');

// ---------- m2b0 call site ----------
var m2b0 = ptr(0x156AE23);
var slotHooked = {};
Interceptor.attach(m2b0, {
  onEnter: function(){
    var edi = this.context.edi;
    var slot = edi.add(0x2B0);
    var target = slot.readPointer();
    emit('M2B0 edi='+edi+' slot='+slot+' target='+target+' -> '+mod(target));
    // dump stack: ret + 4 VARIANTs (16B each) + object
    try{
      var esp = this.context.esp;
      var words=[];
      for(var o=0;o<0x90;o+=4){ words.push('+'+o.toString(16)+':'+esp.add(o).readU32().toString(16)); }
      emit('STACK '+words.join(' '));
    }catch(e){ emit('stack err '+e); }
    // hook the target thunk once
    if(!slotHooked[target.toString()]){
      slotHooked[target.toString()]=1;
      try{
        Interceptor.attach(target, {
          onEnter: function(a){
            emit('THUNK ENTER '+target+' esp='+a[0] ? '' : '');  // placeholder
            this.t = Date.now();
            emit('THUNK ENTER args[0]='+ptr(this.context.esp).readPointer()+' ret='+mod(this.returnAddress));
          },
          onLeave: function(r){ emit('THUNK LEAVE after '+((Date.now()-this.t)/1000).toFixed(2)+'s ret='+r.toInt32()); }
        });
        emit('hooked thunk '+target);
      }catch(e){ emit('hook thunk err '+e); }
    }
  }
});

// ---------- wait / network hooks ----------
function hookExp(modname, name){
  try{
    var m = Process.findModuleByName(modname); if(!m) return;
    var f = m.findExportByName(name); if(!f) return;
    Interceptor.attach(f, { onEnter: function(a){
      emit(name+' from '+mod(this.returnAddress));
    }});
  }catch(e){}
}
hookExp('kernelbase.dll','SleepEx');
hookExp('kernelbase.dll','Sleep');
hookExp('ws2_32.dll','connect');
hookExp('ws2_32.dll','send');
hookExp('ws2_32.dll','recv');
hookExp('winhttp.dll','WinHttpSendRequest');
hookExp('winhttp.dll','WinHttpReceiveResponse');
hookExp('wininet.dll','InternetOpenUrlW');
hookExp('user32.dll','MessageBoxA');
hookExp('user32.dll','MessageBoxW');
hookExp('user32.dll','ShowWindow');
try{
  var vb = Process.findModuleByName('MSVBVM60.DLL');
  var rtc = vb.findExportByName('rtcMsgBox');
  Interceptor.attach(rtc, { onEnter: function(a){ emit('rtcMsgBox from '+mod(this.returnAddress)); } });
}catch(e){}

// ---------- periodic main-thread snapshot ----------
var snapN = 0;
function snapshot(){
  snapN++;
  try{
    var th = Process.enumerateThreads()[0];
    var eip = th.context.eip, esp = th.context.esp, ebp = th.context.ebp;
    emit('SNAP#'+snapN+' eip='+mod(eip)+' esp='+esp+' ebp='+ebp);
    // ebp chain
    var chain=[]; var p = ebp; var guard=0;
    while(!p.isNull() && guard++ < 24){
      var ret = p.add(4).readPointer();
      var mo = modOff(ret);
      if(mo){ chain.push(mo); }
      var next = p.readPointer();
      if(next.compare(p) <= 0) break;  // must move up
      p = next;
    }
    emit('CHAIN '+chain.join(' | '));
  }catch(e){ emit('snap err '+e); }
}
setInterval(snapshot, 1000);

emit('probe ready; exe base='+exeMod.base+' size='+exeMod.size);
