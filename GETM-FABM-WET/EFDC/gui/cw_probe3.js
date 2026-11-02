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
function hook(name) {
  var p = ex('user32.dll', name);
  if (!p) return;
  Interceptor.attach(p, {
    onEnter: function (args) {
      var cls = null;
      try { cls = args[1].readAnsiString(); } catch (e) {}
      if (cls && cls.indexOf('Form') >= 0) {
        var bt = [];
        try { bt = Thread.backtrace(this.context, Backtracer.FUZZY).slice(0, 12).map(where); } catch (e) {}
        send({ api: name, cls: cls, bt: bt });
      }
    }
  });
}
hook('CreateWindowExA');
hook('CreateWindowExW');
