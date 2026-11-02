'use strict';
// diag107.js — 用 Stalker 跟踪 helper(0x156AB70) 的调用流
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(ptr(a)); return m?(m.name+'+0x'+ptr(a).sub(m.base).toString(16)):('0x'+(a>>>0).toString(16)); }catch(e){ return '?'; } }

var started = false;
var seq = [];
Interceptor.attach(ptr(0x156AB70), { onEnter: function(){
  if (started) return;
  started = true;
  var tid = this.threadId;
  emit('helper entered, stalking tid=' + tid);
  try {
    Stalker.follow(tid, {
      events: { call: true, ret: true },
      onReceive: function (events) {
        try {
          var parsed = Stalker.parse(events, { annotate: true, stringify: false });
          for (var i = 0; i < parsed.length; i++) {
            var e = parsed[i];
            if (seq.length < 400) seq.push(e[0] + ' ' + e[1] + '->' + e[2]);
          }
        } catch (err) {}
      }
    });
  } catch (e) { emit('stalker fail: ' + e); }
}});

setTimeout(function(){
  emit('seq length=' + seq.length);
  var start = Math.max(0, seq.length - 120);
  for (var i = start; i < seq.length; i++) emit('  ' + seq[i]);
}, 11000);
emit('diag107 ready');

