'use strict';
function send2(s){ send(s); }
function patchST(p){ try{ p.add(0).writeU16(2018); p.add(2).writeU16(8); p.add(4).writeU16(0); p.add(6).writeU16(1); p.add(8).writeU16(12); p.add(10).writeU16(0); p.add(12).writeU16(0); p.add(14).writeU16(0); }catch(e){} }
setTimeout(function(){
  var k=Process.findModuleByName('kernel32.dll');
  try{ Interceptor.attach(k.findExportByName('GetLocalTime'),{ onEnter:function(a){ this.p=a[0]; }, onLeave:function(){ patchST(this.p); } }); send2('hooked GetLocalTime'); }catch(e){}
  try{ Interceptor.attach(k.findExportByName('GetSystemTime'),{ onEnter:function(a){ this.p=a[0]; }, onLeave:function(){ patchST(this.p); } }); send2('hooked GetSystemTime'); }catch(e){}
  try{ Interceptor.attach(k.findExportByName('GetSystemTimeAsFileTime'),{ onEnter:function(a){ this.p=a[0]; }, onLeave:function(){
      var ft=BigInt('0x01D31D2C00000000'); // 2018-08-01 approx
      try{ this.p.writeU64(ft); }catch(e){}
  } }); send2('hooked GetSystemTimeAsFileTime'); }catch(e){}
}, 200);
send2('loaded');
