'use strict';
function emit(s){ send(s); }
var vb = Process.findModuleByName('MSVBVM60.DLL');
var pErrObj = vb.findExportByName('rtcErrObj');
var ErrObj = new NativeFunction(pErrObj, 'pointer', [], 'stdcall');
var IID_NULL = Memory.alloc(16); IID_NULL.writeByteArray(new Uint8Array(16));

function vstr(v){
  try{ var vt=v.readU16();
    if(vt===8){ var p=v.add(8).readPointer(); return p.isNull()?'':p.readUtf16String(); }
    if(vt===3) return String(v.add(8).readS32());
    return '<vt'+vt+'>';
  }catch(e){ return '<e>'; }
}

function getProp(disp, name){
  var pName = Memory.allocUtf16String(name);
  var arr = Memory.alloc(4); arr.writePointer(pName);
  var dispid = Memory.alloc(4);
  var vt = disp.readPointer();
  var fG = new NativeFunction(vt.add(20).readPointer(), 'int', ['pointer','pointer','pointer','uint','uint','pointer'], 'stdcall');
  var fI = new NativeFunction(vt.add(24).readPointer(), 'int', ['pointer','int','pointer','ushort','pointer','pointer','pointer','pointer'], 'stdcall');
  var hr = fG(disp, IID_NULL, arr, 1, 0, dispid);
  if (hr !== 0) return '<gidn:'+ (hr>>>0).toString(16) +'>';
  var dp = Memory.alloc(16); dp.writePointer(ptr(0)); dp.add(4).writePointer(ptr(0)); dp.add(8).writeU32(0); dp.add(12).writeU32(0);
  var res = Memory.alloc(24); var exc = Memory.alloc(24); var ae = Memory.alloc(4);
  hr = fI(disp, dispid.readS32(), IID_NULL, 2, dp, res, exc, ae);
  if (hr !== 0) return '<inv:'+ (hr>>>0).toString(16) +'>';
  return vstr(res);
}

var u32 = Process.findModuleByName('user32.dll');
Interceptor.attach(u32.findExportByName('SoftModalMessageBox'), { onEnter: function(){
  try{
    var d = ErrObj();
    emit('ErrObj=' + d);
    if (d.isNull()) return;
    emit('Number=' + getProp(d,'Number'));
    emit('Description=' + getProp(d,'Description'));
    emit('Source=' + getProp(d,'Source'));
  }catch(e){ emit('err '+e); }
}});
emit('ready');
