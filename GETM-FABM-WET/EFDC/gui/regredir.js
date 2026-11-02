// Redirect HKCR / HKLM-classes registry writes to HKCU\Software\Classes inside regsvr32.
var HKEY_CLASSES_ROOT = ptr('0x80000000');
var HKEY_CURRENT_USER = ptr('0x80000001');
var HKEY_LOCAL_MACHINE = ptr('0x80000002');

function isHKCU(h) { return h.equals(HKEY_CURRENT_USER); }

function mapSub(hKey, sub) {
  if (!sub || sub.isNull()) return { key: isHKCU(hKey) ? hKey : HKEY_CURRENT_USER, sub: sub };
  var w = sub.readUtf16String();
  var key = hKey;
  if (hKey.equals(HKEY_CLASSES_ROOT)) {
    key = HKEY_CURRENT_USER;
    if (w.toUpperCase().indexOf('SOFTWARE\\CLASSES\\') === 0) w = w.substring(17);
    return { key: key, sub: Memory.allocUtf16String('Software\\Classes\\' + w) };
  }
  if (hKey.equals(HKEY_LOCAL_MACHINE)) {
    key = HKEY_CURRENT_USER;
    var u = w.toUpperCase();
    if (u.indexOf('SOFTWARE\\CLASSES\\') === 0) w = w.substring(17);
    else if (u.indexOf('SOFTWARE\\') === 0) w = 'Software\\Classes\\' + w.substring(9);
    else w = 'Software\\Classes\\' + w;
    return { key: key, sub: Memory.allocUtf16String(w) };
  }
  return { key: key, sub: sub };
}

function mapSubA(hKey, sub) {
  var r = mapSub(hKey, null);
  if (!sub || sub.isNull()) return r.sub;
  var w = sub.readAnsiString();
  if (hKey.equals(HKEY_CLASSES_ROOT) || hKey.equals(HKEY_LOCAL_MACHINE)) {
    var u = w.toUpperCase();
    if (u.indexOf('SOFTWARE\\CLASSES\\') === 0) w = w.substring(17);
    else if (hKey.equals(HKEY_LOCAL_MACHINE) && u.indexOf('SOFTWARE\\') === 0) w = w.substring(9);
    return Memory.allocAnsiString('Software\\Classes\\' + w);
  }
  return sub;
}

function exp(n) { try { return Module.findGlobalExportByName(n); } catch (e) { return null; } }

function redirectW(name) {
  var a = exp(name);
  if (!a) { send({ note: 'missing ' + name }); return; }
  var f = new NativeFunction(a, 'int', ['pointer', 'pointer', 'uint32', 'pointer', 'uint32', 'uint32', 'pointer', 'pointer', 'pointer'], 'stdcall');
  var cb = new NativeCallback(function (hKey, sub, res, cls, opt, sam, sa, phk, disp) {
    var m = mapSub(hKey, sub);
    var r = f(m.key, m.sub, res, cls, opt, sam, sa, phk, disp);
    if (r === 0) send({ reg: name, key: m.sub.readUtf16String() });
    return r;
  }, 'int', ['pointer', 'pointer', 'uint32', 'pointer', 'uint32', 'uint32', 'pointer', 'pointer', 'pointer'], 'stdcall');
  Interceptor.replace(a, cb);
}

function redirectA(name) {
  var a = exp(name);
  if (!a) return;
  var f = new NativeFunction(a, 'int', ['pointer', 'pointer', 'uint32', 'pointer', 'uint32', 'uint32', 'pointer', 'pointer', 'pointer'], 'stdcall');
  var cb = new NativeCallback(function (hKey, sub, res, cls, opt, sam, sa, phk, disp) {
    var ns = mapSubA(hKey, sub);
    return f(hKey.equals(HKEY_CLASSES_ROOT) || hKey.equals(HKEY_LOCAL_MACHINE) ? HKEY_CURRENT_USER : hKey, ns, res, cls, opt, sam, sa, phk, disp);
  }, 'int', ['pointer', 'pointer', 'uint32', 'pointer', 'uint32', 'uint32', 'pointer', 'pointer', 'pointer'], 'stdcall');
  Interceptor.replace(a, cb);
}

function redirectShort(name, wide) {
  var a = exp(name);
  if (!a) { send({ note: 'missing ' + name }); return; }
  var f = new NativeFunction(a, 'int', ['pointer', 'pointer', 'pointer'], 'stdcall');
  var cb = new NativeCallback(function (hKey, sub, phk) {
    var key = hKey;
    var ns = sub;
    if (hKey.equals(HKEY_CLASSES_ROOT) || hKey.equals(HKEY_LOCAL_MACHINE)) {
      key = HKEY_CURRENT_USER;
      ns = wide ? mapSub(hKey, sub).sub : mapSubA(hKey, sub);
    }
    var r = f(key, ns, phk);
    if (r === 0 && ns && !ns.isNull()) { try { send({ reg: name, key: wide ? ns.readUtf16String() : ns.readAnsiString() }); } catch (e) {} }
    return r;
  }, 'int', ['pointer', 'pointer', 'pointer'], 'stdcall');
  Interceptor.replace(a, cb);
}

redirectW('RegCreateKeyExW');
redirectW('RegOpenKeyExW');
redirectA('RegCreateKeyExA');
redirectA('RegOpenKeyExA');
redirectShort('RegOpenKeyA', false);
redirectShort('RegOpenKeyW', true);
redirectShort('RegCreateKeyA', false);
redirectShort('RegCreateKeyW', true);
send({ ready: true });


