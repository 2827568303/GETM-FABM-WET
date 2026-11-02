function where(v) {
  var mods = Process.enumerateModules();
  for (var i = 0; i < mods.length; i++) {
    var m = mods[i];
    if (v.compare(m.base) >= 0 && v.compare(m.base.add(m.size)) < 0)
      return m.name.replace('.pristine', '') + '+0x' + v.sub(m.base).toString(16);
  }
  return v.toString();
}
var t0 = Date.now();
var p = Process.getModuleByName('MSVBVM60.DLL').getExportByName('__vbaNew2');
Interceptor.attach(p, {
  onEnter: function (args) {
    send({ t: Date.now() - t0, fn: '__vbaNew2', arg0: args[0].toString(), objConst: args[1].toString(),
           caller: where(this.returnAddress) });
  }
});
var q = Process.getModuleByName('MSVBVM60.DLL').getExportByName('__vbaNew');
Interceptor.attach(q, {
  onEnter: function (args) {
    send({ t: Date.now() - t0, fn: '__vbaNew', objConst: args[0].toString(),
           caller: where(this.returnAddress) });
  }
});
