// Dump every thread's stack: accurate/fuzzy backtrace + raw stack scan into module ranges.
// No hooks that change behaviour: only reads.
var mods = Process.enumerateModules();
var ranges = mods.map(function (m) { return { n: m.name, b: m.base, e: m.base.add(m.size), s: m.size }; });

function where(v) {
  for (var i = 0; i < ranges.length; i++) {
    var r = ranges[i];
    if (v.compare(r.b) >= 0 && v.compare(r.e) < 0) return r.n + '+0x' + v.sub(r.b).toString(16);
  }
  return null;
}

function sym(a) {
  try { var d = DebugSymbol.fromAddress(a); return d && (d.moduleName || d.name) ? (d.moduleName + '!' + d.name) : ''; }
  catch (e) { return ''; }
}

function dump(tag) {
  var ts = Process.enumerateThreads();
  send({ tag: tag, threads: ts.length, modules: mods.length });
  ts.forEach(function (t) {
    var rec = { tid: t.id, state: t.state, name: t.name || '', eip: null, bt: [], scan: [] };
    try {
      var c = t.context;
      rec.eip = c.pc ? c.pc.toString() : (c.eip ? c.eip.toString() : '?');
      rec.eip_where = where(c.pc || c.eip);
      var sp = c.sp || c.esp;
      var arr = Thread.backtrace(c, Backtracer.FUZZY);
      rec.bt = arr.slice(0, 14).map(function (a) { return where(a) || a.toString(); });
      // raw stack scan
      var p = sp, depth = 0, hits = 0;
      while (depth < 0x1200 && hits < 40) {
        var v;
        try { v = p.readPointer(); } catch (e) { break; }
        var w = where(v);
        if (w) { rec.scan.push(w); hits++; }
        p = p.add(4); depth += 4;
      }
    } catch (e) { rec.err = '' + e; }
    send(rec);
  });
}

setTimeout(function () { dump('t3000'); }, 3000);
setTimeout(function () { dump('t6000'); }, 6000);
setTimeout(function () { dump('t8500'); }, 8500);
