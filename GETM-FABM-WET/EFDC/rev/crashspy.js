'use strict';
var t0 = Date.now();
function ts(){ return (Date.now()-t0).toString().padStart(6,' '); }
function emit(s){ send(ts()+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(ptr(a)); return m?(m.name+'+0x'+ptr(a).sub(m.base).toString(16)):ptr(a).toString(); }catch(e){ return '?'; } }
function wstr(p){ try{ return p.readUtf16String()||''; }catch(e){ return ''; } }

// picture fix
var IID=[0x81,0x09,0xF8,0x7B,0x32,0xBF,0x1A,0x10,0x8B,0xBB,0x00,0xAA,0x00,0x30,0x0C,0xAB];
try{
  var oa=Process.findModuleByName('oleaut32.dll');
  var gdi=Process.findModuleByName('gdi32.dll');
  var CreateBitmap=new NativeFunction(gdi.findExportByName('CreateBitmap'),'pointer',['int','int','uint','uint','pointer']);
  var OleCreate=new NativeFunction(oa.findExportByName('OleCreatePictureIndirect'),'uint',['pointer','pointer','int','pointer']);
  var iid=Memory.alloc(16); iid.writeByteArray(new Uint8Array(IID));
  Interceptor.attach(oa.findExportByName('OleLoadPictureEx'),{
    onEnter:function(a){ this.ppv=a[7]; },
    onLeave:function(r){
      if((r.toInt32()>>>0)===0) return;
      try{ var hbmp=CreateBitmap(2,2,1,1,ptr(0));
        var desc=Memory.alloc(16); desc.writeU32(16); desc.add(4).writeU32(1); desc.add(8).writePointer(hbmp); desc.add(12).writePointer(ptr(0));
        if((OleCreate(desc,iid,1,this.ppv)>>>0)===0) r.replace(ptr(0)); }catch(e){}
    }
  });
  emit('picfix ok');
}catch(e){ emit('picfix ERR '+e); }

var avcount = 0;
Process.setExceptionHandler(function(d){
  if (d.type !== 'access-violation') return false;
  avcount++;
  if (avcount > 3) return false;
  emit('AV#'+avcount+' at '+d.address);
  try{
    var c = d.context;
    emit('  eip='+c.eip+' esp='+c.esp+' ebp='+c.ebp+' eax='+c.eax+' ebx='+c.ebx+' ecx='+c.ecx+' edx='+c.edx+' esi='+c.esi+' edi='+c.edi);
  }catch(e){ emit('  regerr '+e); }
  try{
    var sp = d.context.esp;
    var out = [];
    for (var i=0;i<64;i++){
      var v = 0;
      try { v = sp.add(i*4).readU32(); } catch(e){ break; }
      var tag = '';
      try{ var m = Process.findModuleByAddress(ptr(v)); if (m) tag = m.name+'+0x'+ptr(v).sub(m.base).toString(16); }catch(e){}
      out.push('['+(i*4).toString(16)+'] '+v.toString(16)+(tag?(' '+tag):''));
    }
    emit('  STACK: '+out.join(' ; '));
  }catch(e){ emit('  sterr '+e); }
  try{
    var bt = Thread.backtrace(d.context, Backtracer.ACCURATE).slice(0,20).map(function(a){return mod(a);});
    emit('  ACCURATE: '+bt.join(' <- '));
  }catch(e){ emit('  bterr '+e); }
  return false;
});
emit('ready');
