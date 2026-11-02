// Dump the UI thread's stack while the Activation Wizard is modal, so the call chain
// that opened it is visible. Scans a wide stack window and maps everything to modules.
function where(v) {
  var mods = Process.enumerateModules();
  for (var i = 0; i < mods.length; i++) {
    var m = mods[i];
    if (v.compare(m.base) >= 0 && v.compare(m.base.add(m.size)) < 0) {
      return m.name.replace('.pristine', '') + '+0x' + v.sub(m.base).toString(16);
    }
  }
  return null;
}

function dump(tag) {
  var ts = Process.enumerateThreads();
  var mainTid = null;
  var best = null;
  ts.forEach(function (t) {
    var c = t.context;
    var w = where(c.pc);
    if (w && (w.indexOf('EFDC_Explorer') === 0)) { mainTid = t.id; best = t; }
  });
  if (best === null) {
    // fall back: the thread with the largest stack usage inside user32/VB runtime
    ts.forEach(function (t) { if (best === null) best = t; mainTid = t.id; });
  }
  var rec = { tag: tag, tid: mainTid, eip: best.context.pc.toString(), at: where(best.context.pc) };
  var sp = best.context.sp;
  var chain = [];
  var p = sp, i = 0;
  while (i < 0x4000) {
    var v;
    try { v = p.readPointer(); } catch (e) { break; }
    var w = where(v);
    if (w && w.indexOf('.dll+') < 0 && w.indexOf('ntdll') < 0 && w.indexOf('KERNEL') < 0 &&
        w.indexOf('KERNELBASE') < 0 && w.indexOf('user32') < 0 && w.indexOf('ole32') < 0 &&
        w.indexOf('OLEAUT32') < 0 && w.indexOf('combase') < 0) {
      chain.push('ESP+' + ('0x' + (i * 4).toString(16)) + ' -> ' + w);
    }
    p = p.add(4); i++;
    if (chain.length > 60) break;
  }
  rec.chain = chain;
  send(rec);
}

setTimeout(function () { dump('t4500_splash'); }, 4500);
setTimeout(function () { dump('t7800_wizard'); }, 7800);
setTimeout(function () { dump('t9000_wizard2'); }, 9000);
