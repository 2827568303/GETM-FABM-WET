'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }
var u32=Process.findModuleByName('user32.dll');
function hook(n, timeoutIdx){
  var p=u32.findExportByName(n);
  if(!p){ emit('no '+n); return; }
  Interceptor.attach(p,{onEnter:function(a){
    this.t=Date.now(); this.n=n; this.tid=Process.getCurrentThreadId();
    var cnt=a[0].toInt32();
    var hs=[];
    try{ for(var i=0;i<Math.min(cnt,3);i++) hs.push(a[1].add(i*4).readU32()); }catch(e){}
    this.desc='count='+cnt+' handles='+hs.join(',')+' timeout='+a[timeoutIdx].toInt32();
  },onLeave:function(r){
    var dt=Date.now()-this.t;
    if(Date.now()-t0>2000 && dt>1000) emit(this.n+' '+dt+'ms tid='+this.tid+' '+this.desc+' ret='+(r.toInt32()>>>0)+' from '+mod(this.returnAddress));
  }});
}
hook('MsgWaitForMultipleObjectsEx',2);
hook('MsgWaitForMultipleObjects',3);
emit('ready');
