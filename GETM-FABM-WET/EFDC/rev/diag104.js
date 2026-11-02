'use strict';
// diag104.js — 查询主线程长等待的句柄类型，并尝试 SetEvent 放行
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }

var nt = Process.findModuleByName('ntdll.dll');
var NtQueryObject = new NativeFunction(nt.findExportByName('NtQueryObject'), 'int',
  ['pointer', 'uint', 'pointer', 'uint', 'pointer']);
var SetEvent = new NativeFunction(Process.findModuleByName('kernel32.dll').findExportByName('SetEvent'), 'int', ['pointer']);
var k32 = Process.findModuleByName('kernel32.dll');

function typeName(h){
  var buf = Memory.alloc(512);
  var ret = Memory.alloc(4);
  var st = NtQueryObject(h, 2 /*ObjectTypeInformation*/, buf, 512, ret);
  if (st !== 0) return 'query_fail(0x' + (st >>> 0).toString(16) + ')';
  try {
    var nameLen = buf.readU16();
    var ptr = buf.add(4).readPointer();   // UNICODE_STRING.Buffer 在 +8（32 位结构：Length,MaxLen,Buffer）
    return ptr.readUtf16String();
  } catch (e) { return 'parse_fail'; }
}

function hook(n, cntIdx, arrIdx, toIdx, force){
  var p = k32.findExportByName(n);
  if (!p) return;
  Interceptor.attach(p, {
    onEnter: function(a){
      this.t = Date.now();
      this.n = n;
      this.force = force;
      var cnt = a[cntIdx].toInt32();
      this.hs = [];
      try { for (var i = 0; i < Math.min(cnt, 4); i++) this.hs.push(a[arrIdx].add(i * 4).readPointer()); } catch (e) {}
    },
    onLeave: function(r){
      var dt = Date.now() - this.t;
      if (dt < 1000) return;
      var infos = [];
      for (var i = 0; i < this.hs.length; i++) {
        var t = typeName(this.hs[i]);
        infos.push(this.hs[i] + '(' + t + ')');
      }
      emit(this.n + ' ' + dt + 'ms ' + infos.join(' ; '));
      if (this.force) {
        for (var j = 0; j < this.hs.length; j++) {
          try { var ok = SetEvent(this.hs[j]); emit('  SetEvent(' + this.hs[j] + ') -> ' + ok); } catch (e) {}
        }
      }
    }
  });
}

var FORCE = true; // 由外部注入覆盖
hook('WaitForMultipleObjects', 0, 1, 3, FORCE);
hook('WaitForMultipleObjectsEx', 0, 1, 2, FORCE);
emit('diag104 ready force=' + FORCE);


