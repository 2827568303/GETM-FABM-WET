function where(v) {
  var mods = Process.enumerateModules();
  for (var i = 0; i < mods.length; i++) {
    var m = mods[i];
    if (v.compare(m.base) >= 0 && v.compare(m.base.add(m.size)) < 0)
      return m.name.replace('.pristine', '') + '+0x' + v.sub(m.base).toString(16);
  }
  return v.toString();
}
function ex(mod, name) { try { return Process.getModuleByName(mod).getExportByName(name); } catch (e) { return null; } }
var t0 = Date.now();
function readCls(args, wide) {
  try { return wide ? args[1].readUtf16String() : args[1].readAnsiString(); } catch (e) { return null; }
}
[['CreateWindowExA', false], ['CreateWindowExW', true]].forEach(function (pair) {
  var p = ex('user32.dll', pair[0]);
  if (!p) { send({ err: pair[0] }); return; }
  Interceptor.attach(p, {
    onEnter: function (args) {
      var t = Date.now() - t0;
      var cls = readCls(args, pair[1]);
      if (t > 4000) {
        var bt = [];
        try { bt = Thread.backtrace(this.context, Backtracer.FUZZY).slice(0, 10).map(where); } catch (e) {}
        send({ t: t, api: pair[0], cls: cls, bt: bt });
      }
    }
  });
});
