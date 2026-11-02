'use strict';
// diag105.js — 记录子进程创建（命令行），找出主线程在等的那个子进程
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
var k32 = Process.findModuleByName('kernel32.dll');

['CreateProcessW','CreateProcessA','ShellExecuteW','ShellExecuteExW','WinExec'].forEach(function(n){
  var p = k32.findExportByName(n);
  if (!p) return;
  Interceptor.attach(p, {
    onEnter: function(a){
      var s = n + ' : ';
      try {
        if (n === 'CreateProcessW') s += 'app=' + (a[0].isNull() ? '' : a[0].readUtf16String()) + ' cmd=' + (a[1].isNull() ? '' : a[1].readUtf16String());
        else if (n === 'CreateProcessA') s += 'app=' + (a[0].isNull() ? '' : a[0].readAnsiString()) + ' cmd=' + (a[1].isNull() ? '' : a[1].readAnsiString());
        else if (n === 'ShellExecuteW') s += 'file=' + (a[2].isNull() ? '' : a[2].readUtf16String()) + ' params=' + (a[3].isNull() ? '' : a[3].readUtf16String());
        else if (n === 'WinExec') s += 'cmd=' + a[0].readAnsiString();
        else if (n === 'ShellExecuteExW') s += 'struct=' + a[0];
      } catch (e) { s += '<parse err>'; }
      emit(s);
    }
  });
});
emit('diag105 ready');
