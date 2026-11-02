'use strict';
// diag1.js — 卡死点定性诊断：等待原语 / 网络 / 窗口创建 / RIP 采样
var t0 = Date.now();
function ts(){ return String(Math.round(Date.now()-t0)).padStart(6,' '); }
function emit(s){ send(ts()+' '+s); }
function mod(a){
  try{ var m = Process.findModuleByAddress(a); return m ? (m.name+'+0x'+a.sub(m.base).toString(16)) : a.toString(); }
  catch(e){ return '?'; }
}
function bt(ctx, n){
  try{ return Thread.backtrace(ctx, Backtracer.FUZZY).slice(0, n||10).map(mod).join(' <- '); }
  catch(e){ return '<bt err '+e+'>'; }
}
function hookExp(dll, name, fmt){
  var m = Process.findModuleByName(dll);
  if(!m) return null;
  var p = m.findExportByName(name);
  if(!p) return null;
  Interceptor.attach(p, {
    onEnter: function(a){
      this.t = Date.now();
      try{ emit(fmt(a, this)); }catch(e){ emit(name+' fmt err '+e); }
    },
    onLeave: function(r){
      var dt = Date.now()-this.t;
      if(dt > 300) emit('  ^ '+dll+'!'+name+' RET='+r+' took '+dt+'ms');
    }
  });
  return p;
}

// ---- 1. 等待/休眠原语 ----
hookExp('kernel32.dll','Sleep', function(a,self){ return 'Sleep('+a[0].toInt32()+') from '+mod(self.returnAddress); });
hookExp('kernel32.dll','WaitForSingleObject', function(a,self){ return 'WaitForSingleObject(h='+a[0]+', ms='+a[1].toInt32()+' (0x'+a[1].toInt32().toString(16)+')) from '+mod(self.returnAddress)+' | '+bt(self.context,8); });
hookExp('kernel32.dll','WaitForSingleObjectEx', function(a,self){ return 'WaitForSingleObjectEx(h='+a[0]+', ms='+a[1].toInt32()+') from '+mod(self.returnAddress)+' | '+bt(self.context,8); });
hookExp('user32.dll','MsgWaitForMultipleObjects', function(a,self){ return 'MsgWait(n='+a[0].toInt32()+', ms='+a[3].toInt32()+') from '+mod(self.returnAddress)+' | '+bt(self.context,8); });
hookExp('user32.dll','MsgWaitForMultipleObjectsEx', function(a,self){ return 'MsgWaitEx(n='+a[0].toInt32()+', ms='+a[3].toInt32()+') from '+mod(self.returnAddress)+' | '+bt(self.context,8); });

// ---- 2. 网络 ----
['WinHttpOpen','WinHttpConnect','WinHttpOpenRequest','WinHttpSendRequest','WinHttpReceiveResponse','WinHttpQueryHeaders'].forEach(function(n){
  hookExp('winhttp.dll', n, function(a,self){
    if(n==='WinHttpConnect'){ try{ return 'WinHttpConnect host='+a[1].readUtf16String()+' port='+a[2].toInt32(); }catch(e){} }
    if(n==='WinHttpOpenRequest'){ try{ return 'WinHttpOpenRequest verb='+a[1].readUtf16String()+' path='+a[2].readUtf16String(); }catch(e){} }
    if(n==='WinHttpSendRequest'){ var s='WinHttpSendRequest'; try{ var h=a[3], l=a[4].toInt32(); if(!h.isNull() && l>0 && l<600) s+=' body='+h.readUtf16String(); }catch(e){} return s; }
    return n;
  });
});
['InternetOpenUrlW','HttpOpenRequestW','InternetConnectW','InternetOpenW'].forEach(function(n){
  hookExp('wininet.dll', n, function(a,self){ try{ return n+' '+a[1].readUtf16String(); }catch(e){ return n; } });
});

// ---- 3. 窗口创建 ----
['CreateWindowExW','CreateWindowExA'].forEach(function(n){
  hookExp('user32.dll', n, function(a,self){
    try{
      var cls = n.endsWith('W') ? a[1].readUtf16String() : a[1].readAnsiString();
      var txt = n.endsWith('W') ? (a[2].isNull()?'':a[2].readUtf16String()) : (a[2].isNull()?'':a[2].readAnsiString());
      var ra = mod(self.returnAddress);
      // 只记录来自 exe / MSVBVM60 的窗体类
      if(cls && (/^Thunder|^VB/.test(cls) || /VB6|Form/i.test(cls))){
        return 'CreateWindowEx cls='+cls+' text='+JSON.stringify(txt)+' style=0x'+(a[3].toUInt32()>>>0).toString(16)+' from '+ra;
      }
      return null;
    }catch(e){ return null; }
  });
});

// ---- 4. 对话框/消息框 ----
hookExp('user32.dll','MessageBoxW', function(a,self){ try{ return 'MessageBoxW text='+JSON.stringify(a[1].readUtf16String())+' from '+mod(self.returnAddress)+' | '+bt(self.context,10); }catch(e){ return 'MessageBoxW'; } });
hookExp('user32.dll','MessageBoxIndirectW', function(a,self){
  try{
    var p=a[0], str=ptr(p.add(12).readPointer());
    var cap=ptr(p.add(16).readPointer());
    var txt = p.readU32()===40 ? str.readUtf16String() : ptr(p.add(12).readPointer()).readAnsiString();
    return 'MessageBoxIndirectW text='+JSON.stringify(txt)+' from '+mod(self.returnAddress)+' | '+bt(self.context,10);
  }catch(e){ return 'MessageBoxIndirectW'; }
});

// ---- 5. 文件访问（许可相关）----
hookExp('kernel32.dll','CreateFileW', function(a,self){
  try{
    var f=a[0].readUtf16String();
    if(/\.(lic|bmp|ini|mdb|fno)$/i.test(f) || /DSI|FLEX|licens/i.test(f)) return 'CreateFileW '+f+' from '+mod(self.returnAddress);
  }catch(e){}
  return null;
});

// ---- 6. RIP 采样 ----
var hist = {};
var sampling = true;
var sampler = setInterval(function(){
  if(!sampling) return;
  try{
    var ths = Process.enumerateThreads();
    for(var i=0;i<ths.length;i++){
      var th = ths[i];
      if(th.id !== Process.getCurrentThreadId() && th.context && th.context.pc){
        var k = mod(th.context.pc);
        hist[k] = (hist[k]||0)+1;
      }
    }
  }catch(e){}
}, 40);

rpc.exports = {
  dump: function(){
    sampling = false;
    var arr = Object.keys(hist).map(function(k){ return [k, hist[k]]; });
    arr.sort(function(a,b){ return b[1]-a[1]; });
    return arr.slice(0, 25);
  }
};
emit('diag1 ready');
