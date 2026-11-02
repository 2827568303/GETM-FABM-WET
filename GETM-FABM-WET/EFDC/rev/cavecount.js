'use strict';
function send2(s){ send(s); }
var n=0;
setTimeout(function(){
  var m=Process.findModuleByName('MSVBVM60.DLL');
  var cave=m.base.add(0x105600);
  Interceptor.attach(cave,{ onEnter:function(){ n++; if(n<=5||n%200===0) send2('cave entry #'+n); } });
  send2('counting cave entries');
}, 500);
setTimeout(function(){ send2('total cave entries: '+n); }, 10500);
send2('loaded');
