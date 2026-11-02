function guid(p) {
  try {
    var b = new Uint8Array(p.readByteArray(16));
    function h(n) { return ('0' + n.toString(16)).slice(-2); }
    return ('{' + h(b[3])+h(b[2])+h(b[1])+h(b[0]) + '-' + h(b[5])+h(b[4]) + '-' + h(b[7])+h(b[6]) + '-' +
            h(b[8])+h(b[9]) + '-' + h(b[10])+h(b[11])+h(b[12])+h(b[13])+h(b[14])+h(b[15]) + '}').toUpperCase();
  } catch (e) { return '?'; }
}
function hook(name, clsArg, outArg) {
  var p = Process.getModuleByName('ole32.dll').getExportByName(name);
  if (!p) return;
  Interceptor.attach(p, {
    onEnter: function (args) { this.clsid = guid(args[clsArg]); this.out = args[outArg]; },
    onLeave: function (ret) {
      var hr = ret.toInt32();
      var obj = 'null';
      try { if (hr === 0 && !this.out.isNull()) obj = this.out.readPointer().toString(); } catch (e) {}
      send({ api: name, clsid: this.clsid, hr: hr, obj: obj });
    }
  });
}
hook('CoCreateInstance', 0, 4);
hook('CoGetClassObject', 0, 4);
