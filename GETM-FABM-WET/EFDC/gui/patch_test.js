// Try to neutralise the Activation Wizard creation routine (RVA 0x41bd80) at runtime.
var exe = Process.getModuleByName('EFDC_Explorer8.4.pristine.exe') || Process.getModuleByName('EFDC_Explorer8.4.exe');
var start = exe.base.add(0x41bd80);
var orig = [];
try { orig = Array.prototype.slice.call(new Uint8Array(start.readByteArray(8))); } catch (e) {}
Memory.protect(start, 0x1000, 'rwx');
start.writeByteArray([0xC3]);           // ret
send({ patched: true, at: start.toString(), orig: orig });
// log if it gets called
try {
  Interceptor.attach(exe.base.add(0x41c16a), { onEnter: function () { send({ callerHit: true }); } });
} catch (e) { send({ hookErr: '' + e }); }
