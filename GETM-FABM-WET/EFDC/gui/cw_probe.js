// Prove whether the window-creation hooks fire, and capture app-side callers for form windows.
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
function hook(name, wide) {
  var p = null;
  try { p = Module.getExportByName('user32.dll', name); } catch (e) { send({ err: name + ':' + e }); return; }
  send({ hooked: name, at: p.toString(), mod: Process.findModuleByAddress(p) ? Process.findModuleByAddress(p).name : '?' });
  Interceptor.attach(p, {
    onEnter: function (args) {
      count++;
      var cls = null;
      try { cls = wide ? args[1].readUtf16String() : args[1].readAnsiString(); } catch (e) { cls = '?'; }
      if (count <= 5 || (cls && cls.indexOf('ThunderRT6FormDC') >= 0)) {
        var bt = [];
        try { bt = Thread.backtrace(this.context, Backtracer.FUZZY).slice(0, 10).map(where); } catch (e) {}
        send({ n: count, api: name, cls: cls, style: args[3].toString(), bt: bt });
      }
    }
  });
}
hook('CreateWindowExA', false);
hook('CreateWindowExW', true);
setTimeout(function () { send({ totalCreations: count }); }, 9000);
