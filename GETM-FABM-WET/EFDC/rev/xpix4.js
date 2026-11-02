'use strict';
var t0 = Date.now();
function ts(){ return (Date.now()-t0).toString().padStart(6,' '); }
function emit(s){ send(ts()+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }
function hexbuf(p, n){ var out=[]; for (var i=0;i<n;i++){ try{ out.push(('0'+p.add(i).readU8().toString(16)).slice(-2)); }catch(e){ break; } } return out.join(' '); }

var oa = Process.findModuleByName('oleaut32.dll');
var gdi = Process.findModuleByName('gdi32.dll');
var pLoadEx = oa.findExportByName('OleLoadPictureEx');
var OleCreate = new NativeFunction(oa.findExportByName('OleCreatePictureIndirect'), 'uint', ['pointer','pointer','int','pointer']);
var CreateCompatibleDC = new NativeFunction(gdi.findExportByName('CreateCompatibleDC'), 'pointer', ['pointer']);
var CreateCompatibleBitmap = new NativeFunction(gdi.findExportByName('CreateCompatibleBitmap'), 'pointer', ['pointer','int','int']);
var IID_IPicture = [0x80,0x09,0xF8,0x7B,0x32,0xBF,0x1A,0x10,0x8B,0xBB,0x00,0xAA,0x00,0x30,0x0C,0xAB];

var n = 0;
Interceptor.attach(pLoadEx, {
  onEnter: function(a){ this.out = a[8]; this.riid = a[7]; this.ret = this.returnAddress; },
  onLeave: function(r){
    var hr = r.toInt32()>>>0;
    emit('LoadEx#'+n+' hr=0x'+hr.toString(16)+' out='+this.out);
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
      emit('   subst hr=0x'+(hr2>>>0).toString(16)+' obj='+ppv.readPointer());
      if ((hr2>>>0)===0){ this.out.writePointer(ppv.readPointer()); r.replace(ptr(0)); }
    }catch(e){ emit('   err '+e); }
    n++;
  }
});
var av = 0;
Process.setExceptionHandler(function(d){
  if (d.type !== 'access-violation') return false;
  av++;
  if (av > 2) return false;
  emit('AV at '+d.address);
  try{
    var c = d.context;
    emit('  eip='+c.eip+' esp='+c.esp+' ebp='+c.ebp+' eax='+c.eax+' ebx='+c.ebx+' ecx='+c.ecx+' edx='+c.edx+' esi='+c.esi+' edi='+c.edi);
    var out=[]; var sp=c.esp;
    for (var i=0;i<28;i++){ var v=sp.add(i*4).readU32(); var tag='';
      try{ var m=Process.findModuleByAddress(ptr(v)); if(m) tag='('+m.name+'+0x'+ptr(v).sub(m.base).toString(16)+')'; }catch(e){}
      out.push(v.toString(16)+tag); }
    emit('  STACK: '+out.join(' '));
  }catch(e){ emit('  err '+e); }
  return false;
});
emit('ready v4');
