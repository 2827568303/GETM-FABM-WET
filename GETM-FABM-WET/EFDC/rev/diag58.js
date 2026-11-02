'use strict';
var t0=Date.now();
function emit(s){ send(String(Math.round(Date.now()-t0)).padStart(6,' ')+' '+s); }
function hook(a,n){ try{ Interceptor.attach(ptr(parseInt(a,16)), { onEnter:function(){ emit('HIT '+n+' ('+a+')'); }, onLeave:function(){ emit('  leave '+n); } }); }catch(e){ emit('fail '+n); } }
hook('0x81C4C0','CheckLicensing');
hook('0x81CDBF','SuccessBranch');
hook('0x156AB70','FormHelper');
hook('0x828F50','SplashInit');
hook('0x156ACC0','TitleInit');
emit('ready');
