// 1) module inventory at t=2.5s  2) disassemble the caller regions  3) on AV dump stack+heap
function w(v) {
  var mods = Process.enumerateModules();
  for (var i = 0; i < mods.length; i++) {
    var m = mods[i];
    if (v.compare(m.base) >= 0 && v.compare(m.base.add(m.size)) < 0) return m.name + '+0x' + v.sub(m.base).toString(16);
  }
  return v.toString();
}
function dis(addr, n) {
  var out = [], p = ptr(addr);
  try {
    for (var i = 0; i < n; i++) { var ins = Instruction.parse(p); out.push(p.toString() + '  ' + ins.mnemonic + ' ' + ins.opStr); p = ins.next; }
  } catch (e) { out.push('STOP ' + e); }
  return out;
}
var modsSent = false;
setTimeout(function () {
  var ms = Process.enumerateModules();
  send({ modules: ms.map(function (m) { return m.name + '@' + m.base.toString() + '+' + m.size; }) });
  var exe = Process.enumerateModules()[0];
  send({ tag: 'exe', base: exe.base.toString(), name: exe.name });
  [0x3ac280, 0x2bd220, 0x42a880, 0x250030].forEach(function (rva) {
    send({ dis: 'exe+0x' + rva.toString(16), code: dis(exe.base.add(rva), 16) });
  });
  var vbm = Process.findModuleByName('MSVBVM60.DLL');
  if (vbm) [0x1bfa0, 0x19b6c, 0x19854, 0x1986f, 0x3d529, 0x18501, 0x183cb].forEach(function (rva) {
    send({ dis: 'MSVBVM60+0x' + rva.toString(16), code: dis(vbm.base.add(rva), 8) });
  });
  modsSent = true;
}, 2500);
Process.setExceptionHandler(function (d) {
  if (d.type !== 'access-violation') return false;
  var rec = { av: d.address.toString(), at: w(d.address), eip: d.context.eip.toString(), eipAt: w(d.context.eip),
    regs: { eax: d.context.eax.toString(), ecx: d.context.ecx.toString(), edx: d.context.edx.toString(),
            edi: d.context.edi.toString(), esi: d.context.esi.toString(), ebp: d.context.ebp.toString(),
            esp: d.context.esp.toString() } };
  try { rec.code = dis(d.context.eip, 4); } catch (e) {}
  try { rec.stack = hexdump(d.context.esp, { length: 0x50, ansi: false }); } catch (e) {}
  try { rec.atEdi = hexdump(d.context.edi, { length: 0x40, ansi: false }); } catch (e) {}
  try { rec.atEcx = hexdump(d.context.ecx, { length: 0x40, ansi: false }); } catch (e) {}
  send(rec);
  return false;
});
