'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }
function hx(v){ return ('00000000'+(v>>>0).toString(16)).slice(-8); }
var k32=Process.findModuleByName('kernel32.dll');
Interceptor.attach(k32.findExportByName('RaiseException'),{onEnter:function(a){
  var code=a[0].toUInt32()>>>0;
  if(code!==0xc000008f) return;
  // VB: args[0]=VbErrorInfo*, args[1]=?
  var n=a[2].toInt32(); var parr=a[3];
  var vals=[];
  for(var i=0;i<Math.min(n,3);i++){ try{ vals.push(hx(parr.add(i*4).readU32())); }catch(e){ vals.push('?'); } }
  var num='?';
  try{ var p=parr.isNull()?ptr(0):parr.readPointer(); if(!p.isNull()){ num = p.readU32(); } }catch(e){}
  emit('VBERR code=0x' + code.toString(16) + ' nargs=' + n + ' args=' + vals.join(',') + ' errnum?=' + num);
  try{ emit('  fuz: ' + Thread.backtrace(this.context, Backtracer.FUZZY).slice(0,22).map(mod).join(' <- ')); }catch(e){}
}});
var u32=Process.findModuleByName('user32.dll');
Interceptor.replace(u32.findExportByName('SoftModalMessageBox'), new NativeCallback(function(){ return 1; },'int',['pointer']));
emit('ready');
