// Redirect HKCR (and HKLM\Software\Classes) to HKCU\Software\Classes via RegOverridePredefKey.
var advapi = Module.findGlobalExportByName('RegOverridePredefKey');
var RegOpenKeyExW = new NativeFunction(Module.findGlobalExportByName('RegOpenKeyExW'), 'int',
  ['pointer', 'pointer', 'uint32', 'uint32', 'pointer'], 'stdcall');
var RegOverridePredefKey = new NativeFunction(advapi, 'int', ['pointer', 'pointer'], 'stdcall');
var RegCloseKey = new NativeFunction(Module.findGlobalExportByName('RegCloseKey'), 'int', ['pointer'], 'stdcall');

var HKCU = ptr('0x80000001');
var HKCR = ptr('0x80000000');
var HKLM = ptr('0x80000002');
var KEY_ALL = 0xF003F;

var hk = Memory.alloc(4);
var r1 = RegOpenKeyExW(HKCU, Memory.allocUtf16String('Software\\Classes'), 0, KEY_ALL, hk);
var hClasses = hk.readPointer();
send({ openHKCU: r1, h: hClasses.toString() });

var r2 = RegOverridePredefKey(HKCR, hClasses);
send({ overrideHKCR: r2 });

// HKLM\Software\Classes -> also redirect the HKLM predefined key's "Software\Classes" is not
// separable, so instead we open HKLM's Software\Classes and override HKLM entirely when possible.
var hklmClasses = Memory.alloc(4);
var r3 = RegOpenKeyExW(HKLM, Memory.allocUtf16String('Software\\Classes'), 0, KEY_ALL, hklmClasses);
send({ openHKLM: r3 });
if (r3 === 0) {
  var r4 = RegOverridePredefKey(HKLM, hklmClasses.readPointer());
  send({ overrideHKLM: r4 });
}
send({ ready: true });
