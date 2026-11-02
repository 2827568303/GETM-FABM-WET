// Hook COM activation: log CLSID, HRESULT, and which module owns the returned object's vtable.
function modOf(p) {
  if (!p || p.isNull()) return 'null';
  try {
    var r = Process.findRangeByAddress(p);
    if (!r) return 'unmapped';
    if (r.file && r.file.path) return r.file.path.split('\\').pop() + '+' + p.sub(r.base).toString(16);
    var mods = Process.enumerateModules();
    for (var i = 0; i < mods.length; i++) {
      var m = mods[i];
      if (p.compare(m.base) >= 0 && p.compare(m.base.add(m.size)) < 0) return m.name + '+0x' + p.sub(m.base).toString(16);
    }
    return 'anon@' + r.base.toString() + '+0x' + p.sub(r.base).toString(16) + ' ' + r.protection;
  } catch (e) { return 'err'; }
}
function guidStr(p) {
  try {
    var b = new Uint8Array(p.readByteArray(16));
    function h(n) { return ('0' + n.toString(16)).slice(-2); }
    return '{' + h(b[3]) + h(b[2]) + h(b[1]) + h(b[0]) + '-' + h(b[5]) + h(b[4]) + '-' + h(b[7]) + h(b[6]) + '-' +
      h(b[8]) + h(b[9]) + '-' + h(b[10]) + h(b[11]) + h(b[12]) + h(b[13]) + h(b[14]) + h(b[15]) + '}';
  } catch (e) { return '?'; }
}
function hook(name, clsidArg, outArg) {
  var a = Module.findGlobalExportByName(name) || Module.findExportByName(null, name);
  if (!a) { send({ note: 'no ' + name }); return; }
  Interceptor.attach(a, {
    onEnter: function (args) {
      this.clsid = guidStr(args[clsidArg]);
      this.out = args[outArg];
    },
    onLeave: function (ret) {
      var hr = ret.toInt32() >>> 0;
      var line = name + ' ' + this.clsid + ' hr=0x' + hr.toString(16);
      if (hr === 0) {
        try {
          var obj = this.out.readPointer();
          var vt = obj.readPointer();
          line += ' obj=' + obj + ' vtable=' + vt + ' (' + modOf(vt) + ')';
          try { line += ' vt[0]=' + vt.readPointer() + ' (' + modOf(vt.readPointer()) + ')'; } catch (e) {}
        } catch (e) { line += ' readfail'; }
      }
      send({ com: line });
    }
  });
}
hook('CoCreateInstance', 0, 4);
hook('CoGetClassObject', 0, 4);
var la = Module.findGlobalExportByName('LoadLibraryExW') || Module.findExportByName(null, 'LoadLibraryExW');
if (la) Interceptor.attach(la, { onEnter: function (a) { try { send({ dll: a[0].readUtf16String() }); } catch (e) {} } });
