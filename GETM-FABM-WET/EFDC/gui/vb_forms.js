// Find which VB6 runtime call creates the wizard: hook form/modal related MSVBVM60 exports.
var calls = [];
var mod = Process.findModuleByName('MSVBVM60.DLL');
var names = Process.getModuleByName('MSVBVM60.DLL').enumerateExports().map(function (e) { return e.name; });
var wanted = names.filter(function (n) {
  return /Modal|Form|Thun|__vbaNew|__vbaObjSetAddref|__vbaCastObj|__vbaHresultCheckObj|__vbaFreeObjList/i.test(n);
});
send({ candidates: wanted });

function where(v) {
  var mods = Process.enumerateModules();
  for (var i = 0; i < mods.length; i++) {
    var m = mods[i];
    if (v.compare(m.base) >= 0 && v.compare(m.base.add(m.size)) < 0) return m.name.replace('.pristine', '') + '+0x' + v.sub(m.base).toString(16);
  }
  return v.toString();
}

wanted.forEach(function (n) {
  var a = null;
  try { a = Module.findGlobalExportByName(n); } catch (e) {}
  if (!a) return;
  try {
    Interceptor.attach(a, {
      onEnter: function () {
        var bt = Thread.backtrace(this.context, Backtracer.FUZZY).slice(0, 8).map(where);
        send({ call: n, bt: bt });
      }
    });
  } catch (e) {}
});
send({ ready: true, hooked: wanted.length });

