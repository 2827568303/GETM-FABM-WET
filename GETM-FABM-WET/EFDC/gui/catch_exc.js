// Capture the unhandled AV context, then let it crash (return false) so behaviour is unchanged.
function hex(v) { return v ? v.toString(16) : '?'; }
function regs(c) {
  var o = {};
  if (!c) return o;
  ['pc', 'sp', 'bp', 'eax', 'ebx', 'ecx', 'edx', 'esi', 'edi', 'esp', 'ebp', 'eip'].forEach(function (k) {
    try { if (c[k]) o[k] = c[k].toString(); } catch (e) {}
  });
  return o;
}
function where(v) {
  var mods = Process.enumerateModules();
  for (var i = 0; i < mods.length; i++) {
    var m = mods[i];
    if (v.compare(m.base) >= 0 && v.compare(m.base.add(m.size)) < 0)
      return m.name + '+0x' + v.sub(m.base).toString(16);
  }
  return null;
}
var n = 0;
Process.setExceptionHandler(function (d) {
  n++;
  var rec = { n: n, type: d.type, address: d.address ? d.address.toString() : null,
              atModule: d.address ? where(d.address) : null, regs: regs(d.context) };
  try { rec.bt = Thread.backtrace(d.context, Backtracer.FUZZY).slice(0, 24).map(function (a) { return where(a) || a.toString(); }); } catch (e) { rec.btErr = '' + e; }
  try { rec.description = d.description; } catch (e) {}
  try { rec.code = d.code; } catch (e) {}
  try { rec.mem = d.memory ? d.memory.toString() : null; } catch (e) {}
  send(rec);
  return false; // keep crashing behaviour identical
});
send({ ready: true });
