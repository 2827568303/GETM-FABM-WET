'use strict';
var t0 = Date.now();
function ts(){ return (Date.now()-t0).toString().padStart(6,' '); }
function emit(s){ send(ts()+' '+s); }
function readStr(p){
  try{ var s = p.readUtf16String(); if (s && /^[\x20-\x7E]{2,60}$/.test(s)) return s; }catch(e){}
  try{ var s2 = p.readAnsiString(); if (s2 && /^[\x20-\x7E]{2,60}$/.test(s2)) return s2; }catch(e){}
  return null;
}
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

var base = Process.getModuleByName('EFDC_Explorer8.4.exe').base;
var seen = {};

// VB6 "declared API" resolver: stub does  push <descriptor> ; call 0x451000
try{
  Interceptor.attach(base.add(0x451000 - 0x400000), {
    onEnter: function(a){
      try{
        var desc = this.context.esp.add(4).readPointer();
        var d = desc.toInt32() >>> 0;
        if (seen[d]) return;
        seen[d] = 1;
        var fields = [];
        for (var i=0;i<8;i++){
          var v = 0;
          try { v = desc.add(i*4).readU32(); } catch(e) { break; }
          fields.push(v);
        }
        var strs = [];
        for (var i=0;i<8;i++){
          var v = fields[i];
          if (v > 0x400000 && v < 0x1620000) {
            var s = readStr(ptr(v));
            if (s) strs.push('f'+i+'='+s);
          }
        }
        // sometimes strings live inline right after descriptor
        for (var off=0x10; off<=0x60; off+=4){
          var v2 = 0;
          try { v2 = desc.add(off).readU32(); } catch(e){ break; }
          if (v2 > 0x400000 && v2 < 0x1620000){
            var s2 = readStr(ptr(v2));
            if (s2) strs.push('+'+off.toString(16)+'='+s2);
          }
        }
        emit('API @0x'+d.toString(16)+' fields=['+fields.map(function(x){return '0x'+x.toString(16);}).join(',')+'] '+strs.join(' '));
      }catch(e){ emit('desc err '+e); }
    }
  });
  emit('resolver hook ok');
}catch(e){ emit('resolver hook ERR '+e); }
emit('ready');
