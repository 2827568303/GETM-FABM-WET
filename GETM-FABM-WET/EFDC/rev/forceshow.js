'use strict';
function send2(s){ send(s); }
var T0=Date.now(); function t(){ return ((Date.now()-T0)/1000).toFixed(2); }
setTimeout(function(){
  var u=Process.findModuleByName('user32.dll');
  var ShowWindow=new NativeFunction(u.findExportByName('ShowWindow'),'int',['pointer','int']);
  var IsWindowVisible=new NativeFunction(u.findExportByName('IsWindowVisible'),'int',['pointer']);
  Interceptor.attach(u.findExportByName('CreateWindowExA'),{
    onEnter:function(a){ try{ this.title=a[2].readAnsiString(); }catch(e){ this.title=''; } },
    onLeave:function(r){
      if(this.title && this.title.indexOf('EFDC_Explore')>=0){
        send2('['+t()+'] splash created '+r+' -> ShowWindow');
        var ok=ShowWindow(r,5); // SW_SHOW
        send2('['+t()+'] ShowWindow='+ok+' visible='+IsWindowVisible(r));
      }
    }
  });
  send2('hooked');
}, 150);
send2('loaded');
