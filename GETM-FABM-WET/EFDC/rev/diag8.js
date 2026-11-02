'use strict';
// diag8.js — 抓 user32/win32k 侧的系统调用（主线程消息泵/模态等待）
var t0 = Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }
function bt(ctx){ try{ return Thread.backtrace(ctx, Backtracer.FUZZY).slice(0,10).map(mod).join(' <- '); }catch(e){ return '<bt?>'; } }

function hookMod(dll, name, thr){
  var m = Process.findModuleByName(dll); if(!m) return;
  var p = m.findExportByName(name); if(!p) return;
  Interceptor.attach(p, {
    onEnter: function(a){ this.t = Date.now(); this.tid = Process.getCurrentThreadId(); this.chain = bt(this.context); },
    onLeave: function(r){
      var dt = Date.now() - this.t;
      if (dt >= (thr || 1200)) emit(name+' '+dt+'ms tid='+this.tid+' '+this.chain);
    }
  });
}

['NtUserGetMessage','NtUserWaitMessage','NtUserPeekMessage','NtUserMessageCall','NtUserSendInput'].forEach(function(n){ hookMod('win32u.dll', n, 1200); });
['NtUserGetMessage','NtUserWaitMessage','NtUserPeekMessage'].forEach(function(n){ hookMod('user32.dll', n, 1200); });

// 谁在创建/销毁窗口
var u32 = Process.findModuleByName('user32.dll');
if (u32) {
  ['CreateWindowExW','DestroyWindow','ShowWindow','SetWindowPos'].forEach(function(n){
    var p = u32.findExportByName(n); if(!p) return;
    Interceptor.attach(p, { onEnter: function(a){
      if (n === 'CreateWindowExW') { try{ emit('CreateWindow '+a[1].readUtf16String()+' title='+JSON.stringify(a[2].isNull()?'':a[2].readUtf16String())+' style=0x'+(a[3].toUInt32()>>>0).toString(16)+' from '+mod(this.returnAddress)); }catch(e){} }
      else if (n === 'ShowWindow') { emit('ShowWindow hwnd='+a[0]+' cmd='+a[1].toInt32()+' from '+mod(this.returnAddress)); }
      else if (n === 'DestroyWindow') { emit('DestroyWindow hwnd='+a[0]+' from '+mod(this.returnAddress)); }
      else { try{ emit('SetWindowPos hwnd='+a[0]+' flags=0x'+(a[4].toUInt32()>>>0).toString(16)); }catch(e){} }
    }});
  });
}
emit('diag8 ready');
