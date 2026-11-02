'use strict';
// diag44.js — 在 481 弹框时读取 VB 的 Err 对象（Number/Description/Source）
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }

var vb = Process.findModuleByName('MSVBVM60.DLL');
var rtcErrObj = new NativeFunction(vb.findExportByName('rtcErrObj'), 'pointer', []);
var SysAllocString = new NativeFunction(Process.findModuleByName('oleaut32.dll').findExportByName('SysAllocString'), 'pointer', ['pointer']);

var IID_NULL = Memory.alloc(16);
IID_NULL.writeByteArray(new Uint8Array(16));

function readVariantString(v) {
  try {
    var vt = v.readU16();
    if (vt === 8) {
      var p = v.add(8).readPointer();
      return p.isNull() ? '' : p.readUtf16String();
    }
    if (vt === 3) return String(v.add(8).readS32());
    if (vt === 11) return String(v.add(8).readU16() ? 'True' : 'False');
    return '<vt=' + vt + '>';
  } catch (e) { return '<err ' + e + '>'; }
}

function getProp(disp, name) {
  var pName = Memory.allocUtf16String(name);
  var names = Memory.alloc(4);
  names.writePointer(pName);
  var dispid = Memory.alloc(4);
  var vtbl = disp.readPointer();
  var GetIDsOfNames = new NativeFunction(vtbl.add(5 * 4).readPointer(), 'int', ['pointer', 'pointer', 'pointer', 'uint', 'uint', 'pointer']);
  var Invoke = new NativeFunction(vtbl.add(6 * 4).readPointer(), 'int', ['pointer', 'int', 'pointer', 'ushort', 'pointer', 'pointer', 'pointer', 'pointer']);

  var hr = GetIDsOfNames(disp, IID_NULL, names, 1, 0, dispid);
  if (hr !== 0) return '<gidn hr=0x' + (hr >>> 0).toString(16) + '>';

  var params = Memory.alloc(16);       // DISPPARAMS {rgvarg, rgdispidNamedArgs, cArgs, cNamedArgs}
  params.writePointer(ptr(0));
  params.add(4).writePointer(ptr(0));
  params.add(8).writeU32(0);
  params.add(12).writeU32(0);
  var result = Memory.alloc(24);
  var excep = Memory.alloc(24);
  var argErr = Memory.alloc(4);
  hr = Invoke(disp, dispid.readS32(), IID_NULL, 2 /*PROPERTYGET*/, params, result, excep, argErr);
  if (hr !== 0) return '<invoke hr=0x' + (hr >>> 0).toString(16) + '>';
  return readVariantString(result);
}

var u32 = Process.findModuleByName('user32.dll');
Interceptor.attach(u32.findExportByName('SoftModalMessageBox'), { onEnter: function(){
  try {
    var disp = rtcErrObj();
    if (disp.isNull()) { emit('Err 对象为空'); return; }
    emit('Err.Number      = ' + getProp(disp, 'Number'));
    emit('Err.Description = ' + getProp(disp, 'Description'));
    emit('Err.Source      = ' + getProp(disp, 'Source'));
    emit('Err.HelpFile    = ' + getProp(disp, 'HelpFile'));
    emit('Err.HelpContext = ' + getProp(disp, 'HelpContext'));
  } catch (e) { emit('读 Err 失败: ' + e); }
}});
emit('diag44 ready');
