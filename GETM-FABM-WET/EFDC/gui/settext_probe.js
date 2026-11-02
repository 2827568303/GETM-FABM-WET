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
['SetWindowTextA', 'SetWindowTextW'].forEach(function (n) {
  var p = ex('user32.dll', n);
  if (!p) return;
  Interceptor.attach(p, {
    onEnter: function (args) {
      var t = null;
      try { t = n.endsWith('W') ? args[1].readUtf16String() : args[1].readAnsiString(); } catch (e) {}
      if (t && t.indexOf('Activation Wizard') >= 0) {
        var bt = [];
        try { bt = Thread.backtrace(this.context, Backtracer.FUZZY).slice(0, 18).map(where); } catch (e) {}
        send({ setText: t, hwnd: args[0].toString(), bt: bt });
      }
    }
  });
});
