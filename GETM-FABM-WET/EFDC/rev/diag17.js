'use strict';
// diag17.js — 逐个 Hook CheckLicensing 内部的调用目标，找出「进了不返回」的那个
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function hx(v){ return ('00000000'+(v>>>0).toString(16)).slice(-8); }

var state = {};   // target -> {enters, leaves, lastRA, first, last}

function modname(a){
  try{ var m=Process.findModuleByAddress(ptr(a)); return m?m.name+'+0x'+ptr(a).sub(m.base).toString(16):ptr(a).toString(); }catch(e){ return '?'; }
}

for (var i = 0; i < TARGETS.length; i++) {
  (function(tgt){
    var rec = { enters: 0, leaves: 0, sites: {}, last: 0 };
    state[tgt] = rec;
    try {
      Interceptor.attach(ptr(tgt), {
        onEnter: function(){
          var ra = this.returnAddress;
          var rai = ra.toInt32();
          if (rai >= BODY_START && rai <= BODY_END) {
            rec.enters++;
            rec.last = Date.now();
            rec.sites[hx(rai)] = (rec.sites[hx(rai)] || 0) + 1;
            if (rec.enters <= 3) emit('ENTER ' + hx(tgt) + ' (' + modname(tgt) + ') 来自 site ' + hx(rai));
          }
        },
        onLeave: function(){ rec.leaves++; }
      });
    } catch (e) { emit('attach 失败 ' + hx(tgt) + ': ' + e); }
  })(TARGETS[i]);
}

// 5 秒后开始采样各线程 EIP，看有没有线程停在许可函数体内
var sampled = {};
var iv = setInterval(function(){
  try {
    var ths = Process.enumerateThreads();
    for (var i = 0; i < ths.length; i++) {
      var c = ths[i].context;
      if (!c || !c.pc) continue;
      var pc = c.pc.toInt32();
      if (pc >= BODY_START && pc <= BODY_END && !sampled[pc]) {
        sampled[pc] = 1;
        emit('SAMPLE 线程 ' + ths[i].id + ' EIP=' + hx(pc) + ' (' + modname(pc) + ')');
      }
    }
  } catch (e) {}
}, 400);

setTimeout(function(){
  emit('--- 汇总（进入次数 / 返回次数）---');
  for (var k in state) {
    var r = state[k];
    if (r.enters > 0) emit('  ' + k + '  enter=' + r.enters + ' leave=' + r.leaves + ' sites=' + JSON.stringify(r.sites));
  }
  emit('--- 进入但没返回的 ---');
  for (var k in state) {
    var r = state[k];
    if (r.enters > r.leaves) emit('  BLOCKED ' + k + ' enter=' + r.enters + ' leave=' + r.leaves + ' 最后活动=' + (Date.now() - r.last) + 'ms 前');
  }
}, 15000);
emit('diag17 ready, targets=' + TARGETS.length);
