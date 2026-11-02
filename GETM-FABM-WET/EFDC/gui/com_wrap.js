// Wrap every COM object created via CoCreateInstance/CoGetClassObject with a logging vtable.
// Logs GetIDsOfNames (member name) and Invoke (dispid + return) so we learn the wrapper's surface.
var HKCU = 1;
var logged = {};

function modOf(p) {
  if (!p || p.isNull()) return 'null';
  var mods = Process.enumerateModules();
  for (var i = 0; i < mods.length; i++) {
    var m = mods[i];
    if (p.compare(m.base) >= 0 && p.compare(m.base.add(m.size)) < 0)
      return m.name + '+0x' + p.sub(m.base).toString(16);
  }
  return p.toString();
}

function guid(p) {
  try {
    var b = new Uint8Array(p.readByteArray(16));
    function h(n) { return ('0' + n.toString(16)).slice(-2); }
    return ('{' + h(b[3]) + h(b[2]) + h(b[1]) + h(b[0]) + '-' + h(b[5]) + h(b[4]) + '-' +
            h(b[7]) + h(b[6]) + '-' + h(b[8]) + h(b[9]) + '-' +
            h(b[10]) + h(b[11]) + h(b[12]) + h(b[13]) + h(b[14]) + h(b[15]) + '}').toUpperCase();
  } catch (e) { return '?'; }
}

var WRAPPED = 0;
var KEEP = [];   // must retain callbacks/allocations or they get GC'd

function wrap(obj) {
  try {
    var vt = obj.readPointer();
    if (vt.isNull()) return;
    // already wrapped?
    var marker = vt.sub(0x40);
    try { if (marker.readU32() === 0x57524150) return; } catch (e) {}

    var newVt = Memory.alloc(0x80);
    KEEP.push(newVt);
    for (var i = 0; i < 7; i++) newVt.add(i * 4).writePointer(vt.add(i * 4).readPointer());


    var origGIDN = new NativeFunction(vt.add(5 * 4).readPointer(), 'int',
      ['pointer', 'pointer', 'pointer', 'uint32', 'uint32', 'pointer'], 'stdcall');
    var origInvoke = new NativeFunction(vt.add(6 * 4).readPointer(), 'int',
      ['pointer', 'int32', 'pointer', 'uint32', 'uint16', 'pointer', 'pointer', 'pointer', 'pointer'], 'stdcall');

    var gidn = new NativeCallback(function (pthis, riid, rgszNames, cNames, lcid, rgDispId) {
      var names = [];
      try {
        for (var i = 0; i < cNames; i++) {
          var s = rgszNames.add(i * 4).readPointer();
          names.push(s.isNull() ? 'null' : s.readUtf16String());
        }
      } catch (e) {}
      var hr = origGIDN(pthis, riid, rgszNames, cNames, lcid, rgDispId);
      if (names.length && names[0] && !logged[names[0]]) {
        logged[names[0]] = 1;
        send({ name: names[0], all: names, hr: hr });
      }
      return hr;
    }, 'int', ['pointer', 'pointer', 'pointer', 'uint32', 'uint32', 'pointer'], 'stdcall');

    var invoke = new NativeCallback(function (pthis, dispId, riid, lcid, flags, params, pVarResult, pExcepInfo, puArgErr) {
      var hr = origInvoke(pthis, dispId, riid, lcid, flags, params, pVarResult, pExcepInfo, puArgErr);
      if (flags & 4) { // DISPATCH_METHOD
        var res = '?';
        try {
          if (!pVarResult.isNull()) {
            var vt2 = pVarResult.readU16();
            var val = pVarResult.add(8).readPointer();
            res = 'vt=' + vt2 + ' val=' + val;
          }
        } catch (e) {}
        send({ invoke: dispId, hr: hr, ret: res });
      }
      return hr;
    }, 'int', ['pointer', 'int32', 'pointer', 'uint32', 'uint16', 'pointer', 'pointer', 'pointer', 'pointer'], 'stdcall');

    KEEP.push(gidn); KEEP.push(invoke);
    newVt.add(5 * 4).writePointer(gidn);
    newVt.add(6 * 4).writePointer(invoke);
    obj.writePointer(newVt);
    WRAPPED++;
  } catch (e) { send({ wrapErr: '' + e }); }
}

function hook(name, outArg) {
  var p = Process.getModuleByName('ole32.dll').getExportByName(name);
  if (!p) { send({ err: name }); return; }
  Interceptor.attach(p, {
    onEnter: function (args) { this.out = args[outArg]; this.clsid = guid(args[0]); },
    onLeave: function (ret) {
      if (ret.toInt32() === 0 && !this.out.isNull()) {
        var obj = this.out.readPointer();
        if (!obj.isNull()) { wrap(obj); send({ created: this.clsid, obj: obj.toString() }); }
      }
    }
  });
}
hook('CoCreateInstance', 4);
hook('CoGetClassObject', 4);
setTimeout(function () { send({ wrapped: WRAPPED }); }, 9000);

