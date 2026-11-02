// Show what license state the app actually reads: ini values + DSI registry values.
function wide(p) { try { return p.isNull() ? 'null' : p.readUtf16String(); } catch (e) { return '?'; } }
function ansi(p) { try { return p.isNull() ? 'null' : p.readAnsiString(); } catch (e) { return '?'; } }
function exp(n) { try { return Module.findGlobalExportByName(n); } catch (e) { return null; } }

['GetPrivateProfileStringW', 'GetPrivateProfileStringA'].forEach(function (n) {
  var p = exp(n);
  if (!p) return;
  var isW = n.slice(-1) === 'W';
  Interceptor.attach(p, {
    onEnter: function (args) {
      this.a = [args[1], args[2], args[4], args[5]];
      this.isW = isW;
      this.section = isW ? wide(args[1]) : ansi(args[1]);
      this.key = isW ? wide(args[2]) : ansi(args[2]);
      this.dflt = isW ? wide(args[3]) : ansi(args[3]);
      this.buf = args[4];
      this.file = isW ? wide(args[5]) : ansi(args[5]);
    },
    onLeave: function (r) {
      var v;
      try { v = this.isW ? this.buf.readUtf16String() : this.buf.readAnsiString(); } catch (e) { v = '?'; }
      send({ ini: this.section + '/' + this.key, dflt: this.dflt, got: v, file: this.file });
    }
  });
});

var rq = exp('RegQueryValueExW');
if (rq) Interceptor.attach(rq, {
  onEnter: function (args) {
    this.name = wide(args[1]);
    this.buf = args[4];
  },
  onLeave: function (r) {
    var v = null;
    try { if (this.buf && !this.buf.isNull()) v = this.buf.readUtf16String(); } catch (e) {}
    if (v && v.length < 80) send({ reg: this.name, val: v });
  }
});
send({ ready: true });
