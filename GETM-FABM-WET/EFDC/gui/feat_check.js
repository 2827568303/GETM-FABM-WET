// Disassemble the CheckLicensing tail area and log which branch is taken.
var exe = Process.findModuleByName('EFDC_Explorer8.4.pristine.exe') || Process.findModuleByName('EFDC_Explorer8.4.exe');
send({ base: exe.base.toString(), name: exe.name });
function dis(startRva, n) {
  var out = [], p = exe.base.add(startRva);
  try {
    for (var i = 0; i < n; i++) { var ins = Instruction.parse(p); out.push(p.sub(exe.base).toString() + '  ' + ins.mnemonic + ' ' + ins.opStr); p = ins.next; }
  } catch (e) { out.push('STOP ' + e); }
  return out;
}
send({ region: dis(0x41C9C0, 110) });

[0x41CA01, 0x41CDBF, 0x41D0D3].forEach(function (rva) {
  try {
    Interceptor.attach(exe.base.add(rva), {
      onEnter: function () {
        send({ hit: '0x' + rva.toString(16), eax: this.context.eax.toString(), ebx: this.context.ebx.toString(),
               ecx: this.context.ecx.toString(), edx: this.context.edx.toString(),
               esi: this.context.esi.toString(), edi: this.context.edi.toString() });
      }
    });
  } catch (e) { send({ attachFail: rva.toString(16), err: '' + e }); }
});
