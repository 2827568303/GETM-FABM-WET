// Capture the fatal AV: full context + memory range of the faulting IP + disassembly.
function where(v) {
  var mods = Process.enumerateModules();
  for (var i = 0; i < mods.length; i++) {
    var m = mods[i];
    if (v.compare(m.base) >= 0 && v.compare(m.base.add(m.size)) < 0)
      return m.name + '+0x' + v.sub(m.base).toString(16);
  }
  return null;
}
function regs(c) {
  var o = {};
  ['eip', 'esp', 'ebp', 'eax', 'ebx', 'ecx', 'edx', 'esi', 'edi', 'eflags'].forEach(function (k) {
    try { if (c[k]) o[k] = c[k].toString(); } catch (e) {}
  });
  return o;
}
var last = null;
Process.setExceptionHandler(function (d) {
  var rec = { type: d.type, addr: d.address.toString(), at: where(d.address), regs: regs(d.context) };
  try { rec.bt = Thread.backtrace(d.context, Backtracer.FUZZY).slice(0, 18).map(function (a) { return where(a) || a.toString(); }); } catch (e) {}
  if (d.type === 'access-violation') {
    try {
      var r = Process.findRangeByAddress(d.address);
      rec.range = r ? { base: r.base.toString(), size: r.size, prot: r.protection, file: r.file ? r.file.path : null } : null;
    } catch (e) {}
    try { rec.disasm = Instruction.parse(d.context.eip).toString(); } catch (e) { rec.disasm = 'n/a'; }
    try {
      var e = d.context.eip;
      var out = [];
      for (var i = 0; i < 8; i++) {
        var ins = Instruction.parse(e);
        out.push(e.toString() + '  ' + ins.mnemonic + ' ' + ins.opStr);
        e = ins.next;
      }
      rec.code = out;
    } catch (e) {}
    try { rec.stack = d.context.esp.readByteArray(0x60); } catch (e) {}
    send(rec);
    last = d.context.eip;
    return false;
  }
  return false;
});
setTimeout(function () { send({ alive: true }); }, 6000);
