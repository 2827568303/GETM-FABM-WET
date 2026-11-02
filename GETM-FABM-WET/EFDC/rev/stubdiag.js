'use strict';
function send2(s){ send(s); }
function hookExp(mod,fn,onEnter,onLeave){ var m=Process.findModuleByName(mod); if(!m) return; var p=m.findExportByName(fn); if(!p) return;
  try{ Interceptor.attach(p,{onEnter:onEnter,onLeave:onLeave}); send2('hooked '+fn); }catch(e){ send2('fail '+fn); } }
setTimeout(function(){
  var m=Process.findModuleByName('MSVBVM60.DLL');
  var cave=m.base.add(0x105600);
  try{ Interceptor.attach(cave,{ onEnter:function(){ send2('ENTER cave ebp='+this.context.ebp); }, onLeave:function(r){ send2('LEAVE cave eax=0x'+(r.toInt32()>>>0).toString(16)); } }); send2('hooked cave'); }catch(e){ send2('cave err '+e); }
  hookExp('gdi32.dll','CreateBitmap',function(a){ this.w=a[0].toInt32(); this.h=a[1].toInt32(); this.p=a[2].toInt32(); this.b=a[3].toInt32(); },function(r){ send2('CreateBitmap('+this.w+','+this.h+','+this.p+','+this.b+') -> '+r); });
  hookExp('oleaut32.dll','OleCreatePictureIndirect',function(a){ this.d=a[0]; this.iid=a[1]; this.own=a[2].toInt32(); this.ppv=a[3]; },function(r){ send2('OleCreatePictureIndirect own='+this.own+' ppv='+this.ppv+' -> 0x'+(r.toInt32()>>>0).toString(16)); });
}, 600);
send2('loaded');
