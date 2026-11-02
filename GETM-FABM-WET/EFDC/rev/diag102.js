'use strict';
// diag102.js — hook FNP_Act_Installer 的所有导出，找出卡住的那个调用
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }

function install(){
  var m = Process.findModuleByName('FNP_Act_Installer.dll');
  if (!m) { emit('FNP not loaded'); return; }
  var exps = m.enumerateExports();
  emit('FNP exports: ' + exps.length);
  var n = 0;
  exps.forEach(function(e){
    if (e.type !== 'function' || !e.address) return;
    try {
      Interceptor.attach(e.address, {
        onEnter: function(){ this.t = Date.now(); },
        onLeave: function(r){
          var dt = Date.now() - this.t;
          if (dt > 800) emit('FNP_' + e.name + ' ' + dt + 'ms ret=' + (r.toInt32() >>> 0));
        }
      });
      n++;
    } catch (err) {}
  });
  emit('hooked ' + n + ' FNP exports');
}

var tries = 0;
var iv = setInterval(function(){
  tries++;
  var m = Process.findModuleByName('FNP_Act_Installer.dll');
  if (m) { clearInterval(iv); install(); }
  else if (tries > 40) { clearInterval(iv); emit('FNP never loaded'); }
}, 100);
emit('diag102 ready');
