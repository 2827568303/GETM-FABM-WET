// Log every registry API call with path (no modification) to discover which one regsvr32 uses.
function exp(n) {
  try { return Module.findGlobalExportByName(n); } catch (e) { return null; }
}
function w(p) { try { return p.isNull() ? 'null' : p.readUtf16String(); } catch (e) { return '?'; } }
function a(p) { try { return p.isNull() ? 'null' : p.readAnsiString(); } catch (e) { return '?'; } }

var singles = ['RegCreateKeyExW', 'RegCreateKeyExA', 'RegOpenKeyExW', 'RegOpenKeyExA',
               'RegCreateKeyW', 'RegCreateKeyA', 'RegOpenKeyW', 'RegOpenKeyA',
               'RegDeleteKeyW', 'RegDeleteKeyA', 'RegQueryInfoKeyW', 'RegQueryValueExW', 'RegQueryValueExA'];
singles.forEach(function (n) {
  var p = exp(n);
  if (!p) { send({ miss: n }); return; }
  try {
    Interceptor.attach(p, {
      onEnter: function (args) {
        var s = null;
        try { s = (n.slice(-1) === 'W') ? w(args[1]) : a(args[1]); } catch (e) { s = '?'; }
        send({ call: n, hkey: args[0].toString(), sub: s });
      },
      onLeave: function (r) { send({ ret: n, hr: r.toInt32() }); }
    });
  } catch (e) { send({ err: n + ': ' + e }); }
});
send({ ready: true });
