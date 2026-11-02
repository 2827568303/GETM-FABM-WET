// Ring-buffer the last meaningful Win32 calls, then dump on the fatal AV.
var buf = [];
var MAX = 80;

function push(s) {
  var t = Date.now() % 100000;
  buf.push(t + ' ' + s);
  if (buf.length > MAX) buf.shift();
}
function exp(n) {
  try { return Module.findGlobalExportByName(n); } catch (e) {}
  try { return Module.findExportByName(null, n); } catch (e) {}
  return null;
}
function wide(p) { try { return p.isNull() ? 'null' : p.readUtf16String(); } catch (e) { return '?'; } }
function ansi(p) { try { return p.isNull() ? 'null' : p.readAnsiString(); } catch (e) { return '?'; } }

var hooks = [
  ['CreateFileW', 1, function (a) { return 'CreateFileW ' + wide(a[0]); }],
  ['RegOpenKeyExW', 2, function (a) { return 'RegOpenKey ' + wide(a[1]); }],
  ['RegQueryValueExW', 2, function (a) { return 'RegQuery ' + wide(a[1]); }],
  ['CreateWindowExW', 9, function (a) { return 'CreateWindowEx cls=' + wide(a[1]) + ' name=' + wide(a[2]); }],
  ['MessageBoxW', 2, function (a) { return 'MessageBox text=' + wide(a[1]) + ' cap=' + wide(a[2]); }],
  ['DialogBoxParamW', 2, function (a) { return 'DialogBoxParam'; }],
  ['CreateProcessW', 2, function (a) { return 'CreateProcess ' + wide(a[0]); }],
  ['ShellExecuteExW', 1, function (a) { return 'ShellExecuteEx'; }],
  ['InternetOpenW', 1, function (a) { return 'InternetOpen ' + wide(a[0]); }],
  ['InternetOpenUrlW', 2, function (a) { return 'InternetOpenUrl ' + wide(a[1]); }],
  ['WinHttpOpen', 1, function (a) { return 'WinHttpOpen ' + wide(a[0]); }],
  ['CoCreateInstance', 1, function (a) {
    try { return 'CoCreateInstance ' + a[0].readByteArray(16); } catch (e) { return 'CoCreateInstance'; }
  }],
  ['LoadLibraryW', 1, function (a) { return 'LoadLibrary ' + wide(a[0]); }],
  ['GetProcAddress', 2, function (a) { return 'GetProcAddress ' + ansi(a[1]); }]
];

hooks.forEach(function (h) {
  var addr = exp(h[0]);
  if (!addr) { push('(no export) ' + h[0]); return; }
  try {
    Interceptor.attach(addr, {
      onEnter: function (args) {
        try { push(h[2](args)); } catch (e) { push(h[0] + ' <err>'); }
      }
    });
  } catch (e) { push('hook fail ' + h[0] + ': ' + e); }
});

function dis(addr, n) {
  var out = [], p = ptr(addr);
  for (var i = 0; i < n; i++) { var ins = Instruction.parse(p); out.push(p + '  ' + ins.mnemonic + ' ' + ins.opStr); p = ins.next; }
  return out;
}

Process.setExceptionHandler(function (d) {
  if (d.type !== 'access-violation') return false;
  var rec = { av: d.address.toString(), eip: d.context.eip.toString(),
    regs: { eax: d.context.eax.toString(), ecx: d.context.ecx.toString(), edx: d.context.edx.toString(),
            ebx: d.context.ebx.toString(), esi: d.context.esi.toString(), edi: d.context.edi.toString(),
            ebp: d.context.ebp.toString(), esp: d.context.esp.toString() } };
  rec.trace = buf.slice();
  try {
    var vbm = Process.findModuleByName('MSVBVM60.DLL');
    rec.callSite = dis(vbm.base.add(0x1bf40), 22);
    try { rec.vtablePtr = ptr(d.context.ecx).readPointer().toString(); } catch (e) { rec.vtablePtr = 'unreadable'; }
    try {
      var vt = ptr(d.context.ecx).readPointer();
      rec.vtable0 = hexdump(vt, { length: 0x20 });
    } catch (e) {}
  } catch (e) { rec.err = '' + e; }
  send(rec);
  return false;
});
