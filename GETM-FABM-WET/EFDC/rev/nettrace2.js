'use strict';
function send2(s){ send(s); }
var T0=Date.now(); function t(){ return ((Date.now()-T0)/1000).toFixed(2); }
function wstr(p){ try{ return p.isNull()?'':p.readUtf16String(); }catch(e){ return '?'; } }
function astr(p){ try{ return p.isNull()?'':p.readAnsiString(); }catch(e){ return '?'; } }
var done={};
function tryHook(mod,fn,cb){
  var key=mod+'!'+fn; if(done[key]) return;
  var m=Process.findModuleByName(mod); if(!m) return;
  var p=m.findExportByName(fn); if(!p) return;
  try{ Interceptor.attach(p,cb); done[key]=1; send2('hooked '+key); }catch(e){ done[key]=1; send2('fail '+key+' '+e); }
}
var iv=setInterval(function(){
  tryHook('winhttp.dll','WinHttpConnect',{onEnter:function(a){ send2('['+t()+'] WinHttpConnect '+JSON.stringify(wstr(a[1]))+':'+a[2].toInt32()); }});
  tryHook('winhttp.dll','WinHttpOpenRequest',{onEnter:function(a){ send2('['+t()+'] WinHttpOpenRequest '+JSON.stringify(wstr(a[1]))+' '+JSON.stringify(wstr(a[2]))); }});
  tryHook('winhttp.dll','WinHttpSendRequest',{onEnter:function(){ send2('['+t()+'] WinHttpSendRequest'); }});
  tryHook('winhttp.dll','WinHttpReceiveResponse',{onEnter:function(){ send2('['+t()+'] WinHttpReceiveResponse'); }});
  ['InternetOpenUrlA','InternetOpenUrlW','HttpOpenRequestA','InternetConnectA'].forEach(function(fn){
    tryHook('wininet.dll',fn,{onEnter:function(a){ var s=/W$/.test(fn)?wstr(a[1]):astr(a[1]); send2('['+t()+'] '+fn+' '+JSON.stringify(s)); }});
  });
}, 200);
setTimeout(function(){ clearInterval(iv); send2('stop polling'); }, 12000);
send2('loaded');
