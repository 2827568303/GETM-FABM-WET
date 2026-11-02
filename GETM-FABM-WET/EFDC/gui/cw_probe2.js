function where(v) {
  var mods = Process.enumerateModules();
  for (var i = 0; i < mods.length; i++) {
    var m = mods[i];
    if (v.compare(m.base) >= 0 && v.compare(m.base.add(m.size)) < 0)
      return m.name.replace('.pristine', '') + '+0x' + v.sub(m.base).toString(16);
  }
  return v.toString();
}
var count = 0;
function ex(mod, name) {
  try { return Process.getModuleByName(mod).getExportByName(name); } catch (e) { return null; }
}
function hook(mod, name, wide) {
  var p = ex(mod, name);
  if (!p) { send({ err: mod + '!' + name }); return; }
  send({ hooked: mod + '!' + name, at: p.toString() });
  Interceptor.attach(p, {
    onEnter: function (args) {
      count++;
      var cls = null;
      try { cls = wide ? args[1].readUtf16String() : args[1].readAnsiString(); } catch (e) { cls = '?'; }
      if (count <= 3 || (cls && cls.indexOf('ThunderRT6FormDC') >= 0)) {
        var bt = [];
        try { bt = Thread.backtrace(this.context, Backtracer.FUZZY).slice(0, 10).map(where); } catch (e) {}
        send({ n: count, api: name, cls: cls, bt: bt });
      }
    }
  });
}
hook('user32.dll', 'CreateWindowExA', false);
hook('user32.dll', 'CreateWindowExW', true);
setTimeout(function () { send({ totalCreations: count }); }, 9000);
