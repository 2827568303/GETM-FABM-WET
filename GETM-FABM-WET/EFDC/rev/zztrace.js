'use strict';
var t0 = Date.now();
function ts(){ return (Date.now()-t0).toString().padStart(6,' '); }
function emit(s){ send(ts()+' '+s); }
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
}catch(e){ emit('picfix ERR '+e); }

var base = Process.getModuleByName('EFDC_Explorer8.4.exe').base;
var T = [0x81a800,0x81bba0,0x81bf50,0x81d0f0,0x81d3e0,0x81de90,0x81eda0,0x81f020,0x820200,0x820b10,
         0x821130,0x822450,0x828f50,0x829650,0x829950,0x82ace0,0x82c230,0x82c950,0x82e160,0x82e240,
         0x82e280,0x82e2c0,0x832420,0x836680,0x156a820,0x156a880,0x156ab70];
var depth = 0;
T.forEach(function(va){
  var a = base.add(va - 0x400000);
  Interceptor.attach(a, {
    onEnter: function(){
      depth++;
      this.d = depth;
      emit('  '.repeat(Math.min(depth,12)) + 'ENTER 0x'+va.toString(16));
    },
    onLeave: function(r){
      emit('  '.repeat(Math.min(depth,12)) + 'LEAVE 0x'+va.toString(16)+' -> 0x'+(r.toInt32()>>>0).toString(16));
      depth--;
    }
  });
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
    var out=[];
    var sp=c.esp;
    for (var i=0;i<40;i++){ var v=sp.add(i*4).readU32(); var tag='';
      try{ var m=Process.findModuleByAddress(ptr(v)); if(m) tag=m.name+'+0x'+ptr(v).sub(m.base).toString(16); }catch(e){}
      out.push(v.toString(16)+ (tag?'('+tag+')':'')); }
    emit('  STACK: '+out.join(' '));
  }catch(e){ emit('  err '+e); }
  return false;
});
emit('ready, hooks='+T.length);
