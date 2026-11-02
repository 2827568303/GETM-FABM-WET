'use strict';
// diag3.js — 让所有网络连接立即失败（不挂起），观察程序是否因此继续
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }

// 1) 禁掉 TCP 连接
var ws2 = Process.findModuleByName('ws2_32.dll');
if (ws2) {
  var pConnect = ws2.findExportByName('connect');
  Interceptor.attach(pConnect, {
    onEnter: function(a){
      try{
        var sa = a[1];
        var fam = sa.readU16();
        var ip = '', port = 0;
        if (fam === 2) {
          port = (sa.add(2).readU8() << 8) | sa.add(3).readU8();
          ip = [0,1,2,3].map(function(i){ return sa.add(4+i).readU8(); }).join('.');
        }
        emit('CONNECT ' + ip + ':' + port + ' -> FAIL(10061) from ' + mod(this.returnAddress));
      }catch(e){ emit('CONNECT ?'); }
    },
    onLeave: function(r){
      try{ r.replace(ptr(-1)); }catch(e){}
      this.errnoSet = true;
    }
  });
  var pWSA = ws2.findExportByName('WSAGetLastError');
}

// 2) WinHTTP 直接失败
function failFn(dll, name, retVal){
  var m = Process.findModuleByName(dll); if(!m) return;
  var p = m.findExportByName(name); if(!p) return;
  Interceptor.attach(p, { onEnter: function(){ emit(name+' -> fail from '+mod(this.returnAddress)); },
                          onLeave: function(r){ r.replace(ptr(retVal)); } });
}
failFn('WINHTTP.dll','WinHttpConnect', 0);
failFn('WINHTTP.dll','WinHttpOpenRequest', 0);

// 3) WinINet
failFn('wininet.dll','InternetConnectW', 0);
failFn('wininet.dll','InternetOpenUrlW', 0);

// 4) msxml（COM 层不好 Hook），改为监控
var ole = Process.findModuleByName('ole32.dll');
if (ole) {
  var pCCI = ole.findExportByName('CoCreateInstance');
  Interceptor.attach(pCCI, { onEnter: function(a){
    try{ var u=new Uint8Array(a[0].readByteArray(16)); emit('CoCreate '+Array.from(u).map(function(x){return x.toString(16).padStart(2,'0');}).join('')); }catch(e){}
  }});
}
emit('diag3 ready (network blocking)');
