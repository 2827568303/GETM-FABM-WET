'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
var ws=Process.findModuleByName('ws2_32.dll');
if(ws){
  var p=ws.findExportByName('connect');
  Interceptor.attach(p,{onEnter:function(a){
    try{
      var sa=a[1];
      var fam=sa.readU16();
      var ip='',port=0;
      if(fam===2){ port=(sa.add(2).readU8()<<8)|sa.add(3).readU8(); ip=[0,1,2,3].map(function(i){return sa.add(4+i).readU8();}).join('.'); }
      emit('connect '+ip+':'+port);
    }catch(e){ emit('connect ?'); }
  }});
}
var w32=Process.findModuleByName('winhttp.dll');
if(!w32){ setTimeout(function(){
  var m=Process.findModuleByName('winhttp.dll');
  if(m) emit('winhttp loaded later');
},2000); }
emit('ready');
