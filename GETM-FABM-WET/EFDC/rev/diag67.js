'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
var u32=Process.findModuleByName('user32.dll');
var GetMessageW=u32.findExportByName('GetMessageW');
var PeekMessageW=u32.findExportByName('PeekMessageW');
var counts={};
['DispatchMessageW','PeekMessageW','GetMessageW'].forEach(function(n){
  var p=u32.findExportByName(n);
  Interceptor.attach(p,{onEnter:function(a){
    var msg = (n==='DispatchMessageW') ? a[0] : a[0];
    try{ var id=msg.readU32(); counts[id]=(counts[id]||0)+1; }catch(e){}
  }});
});
setTimeout(function(){
  var arr=Object.keys(counts).map(function(k){return [parseInt(k),counts[k]];});
  arr.sort(function(a,b){return b[1]-a[1];});
  emit('--- message histogram ---');
  for(var i=0;i<Math.min(12,arr.length);i++) emit('  msg 0x'+arr[i][0].toString(16)+'  x'+arr[i][1]);
}, 9000);
emit('ready');
