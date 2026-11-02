'use strict';
// diag2.js — 轻量：只抓 HTTP 请求 URL 与消息框，不干扰时序
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }
function s(p){ try{ return p.isNull()?'':p.readUtf16String(); }catch(e){ return '<bad>'; } }

function hookMod(dll, name, fmt){
  var m = Process.findModuleByName(dll); if(!m) return;
  var p = m.findExportByName(name); if(!p) return;
  Interceptor.attach(p, { onEnter: function(a){ try{ var r = fmt(a, this); if(r) emit(r); }catch(e){ emit(name+' ERR '+e); } } });
}

hookMod('WINHTTP.dll','WinHttpConnect', function(a){ return 'HTTP connect host='+s(a[1])+' port='+a[2].toInt32(); });
hookMod('WINHTTP.dll','WinHttpOpenRequest', function(a){ return 'HTTP open verb='+s(a[1])+' path='+s(a[2]); });
hookMod('WINHTTP.dll','WinHttpSendRequest', function(a){ return 'HTTP send hdr='+s(a[0])+' from '+mod(this.returnAddress); });
hookMod('WINHTTP.dll','WinHttpReceiveResponse', function(a){ return 'HTTP recv'; });
hookMod('WINHTTP.dll','WinHttpQueryHeaders', function(a,self){
  // 读取返回头缓冲
  return 'HTTP queryHeaders from '+mod(self.returnAddress);
});
hookMod('WINHTTP.dll','WinHttpReadData', function(a,self){
  this.buf=a[1]; this.len=a[2].toInt32();
  this.ra=mod(self.returnAddress);
});
hookMod('wininet.dll','HttpSendRequestW', function(a){ return 'INET send '+s(a[0]); });
hookMod('wininet.dll','InternetOpenUrlW', function(a){ return 'INET open '+s(a[1]); });
hookMod('urlmon.dll','URLDownloadToFileW', function(a){ return 'URLMON '+s(a[1]); });
hookMod('ole32.dll','CoCreateInstance', function(a,self){
  try{
    var g = a[0].readByteArray(16); var u = new Uint8Array(g);
    var hex = Array.from(u).map(function(x){ return x.toString(16).padStart(2,'0'); }).join('');
    return 'CoCreate '+hex+' from '+mod(self.returnAddress);
  }catch(e){}
});
hookMod('user32.dll','MessageBoxW', function(a){ return 'MSGBOX '+s(a[1])+' | '+s(a[2]); });
emit('diag2 ready');
