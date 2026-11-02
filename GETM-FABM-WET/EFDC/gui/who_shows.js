// Log top-level form creation with caller backtrace, so we can find the code that
// instantiates / shows the Activation Wizard.
function where(v) {
  var mods = Process.enumerateModules();
  for (var i = 0; i < mods.length; i++) {
    var m = mods[i];
    if (v.compare(m.base) >= 0 && v.compare(m.base.add(m.size)) < 0) return m.name + '+0x' + v.sub(m.base).toString(16);
  }
  return v.toString();
}
var cw = Module.findGlobalExportByName('CreateWindowExW');
Interceptor.attach(cw, {
  onEnter: function (args) {
    this.cls = null; this.name = null;
    try { this.cls = args[1].readUtf16String(); } catch (e) {}
    try { this.name = args[2].readUtf16String(); } catch (e) {}
    if (this.cls && this.cls.indexOf('ThunderRT6FormDC') >= 0) {
      var bt = Thread.backtrace(this.context, Backtracer.FUZZY).slice(0, 12).map(where);
      send({ form: this.cls, name: this.name, exstyle: args[0].toString(), style: args[3].toString(), bt: bt });
    }
  },
  onLeave: function (r) {
    if (this.cls && this.cls.indexOf('ThunderRT6FormDC') >= 0) send({ created: this.name, hwnd: r.toString() });
  }
});
// Also log modal dialog entry points
['MessageBoxW', 'DialogBoxParamW'].forEach(function (n) {
  var p = Module.findGlobalExportByName(n);
  if (p) Interceptor.attach(p, { onEnter: function () { send({ dlg: n, bt: Thread.backtrace(this.context, Backtracer.FUZZY).slice(0, 10).map(where) }); } });
});
send({ ready: true });
