// VB6 is an ANSI app: hook CreateWindowExA too, and log caller backtraces for form windows.
function where(v) {
  var mods = Process.enumerateModules();
  for (var i = 0; i < mods.length; i++) {
    var m = mods[i];
    if (v.compare(m.base) >= 0 && v.compare(m.base.add(m.size)) < 0) return m.name + '+0x' + v.sub(m.base).toString(16);
  }
  return v.toString();
}
function hookA() {
  var p = Module.findGlobalExportByName('CreateWindowExA');
  Interceptor.attach(p, {
    onEnter: function (args) {
      this.cls = null; this.name = null;
      try { this.cls = args[1].readAnsiString(); } catch (e) {}
      try { this.name = args[2].readAnsiString(); } catch (e) {}
      if (this.cls && this.cls.indexOf('ThunderRT6Form') >= 0) {
        send({ formA: this.cls, name: this.name, style: args[3].toString(),
               bt: Thread.backtrace(this.context, Backtracer.FUZZY).slice(0, 12).map(where) });
      }
    }
  });
}
function hookW() {
  var p = Module.findGlobalExportByName('CreateWindowExW');
  Interceptor.attach(p, {
    onEnter: function (args) {
      this.cls = null; this.name = null;
      try { this.cls = args[1].readUtf16String(); } catch (e) {}
      try { this.name = args[2].readUtf16String(); } catch (e) {}
      if (this.cls && this.cls.indexOf('ThunderRT6Form') >= 0) {
        send({ formW: this.cls, name: this.name, style: args[3].toString(),
               bt: Thread.backtrace(this.context, Backtracer.FUZZY).slice(0, 12).map(where) });
      }
    }
  });
}
hookA(); hookW();
send({ ready: true });
