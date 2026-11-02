'use strict';
function send2(s){ send(s); }
function g(s){ var m=s.replace(/[{}]/g,'').split('-'); var b=new Uint8Array(16);
  var d1=parseInt(m[0],16),d2=parseInt(m[1],16),d3=parseInt(m[2],16);
  b[0]=d1&255;b[1]=(d1>>8)&255;b[2]=(d1>>16)&255;b[3]=(d1>>>24)&255;
  b[4]=d2&255;b[5]=(d2>>8)&255;b[6]=d3&255;b[7]=(d3>>8)&255;
  for(var i=0;i<4;i++) b[8+i]=parseInt(m[3].substr(i*2,2),16);
  for(var i=0;i<8;i++) b[12+i]=parseInt(m[4].substr(i*2,2),16);
  return b; }
setTimeout(function(){
  try{
    var ole32=Process.findModuleByName('ole32.dll');
    var CoInit=new NativeFunction(ole32.findExportByName('CoInitializeEx'),'int',['pointer','uint']);
    var CCI=new NativeFunction(ole32.findExportByName('CoCreateInstance'),'uint',['pointer','pointer','uint','pointer','pointer']);
    send2('CoInitializeEx(STA)=0x'+((CoInit(ptr(0),2)>>>0).toString(16)));
    var tests=[['WICImagingFactory','{CACAF262-9370-4615-A13B-9F5539DA4C0A}','{EC5EC8A9-C395-4314-9C77-54D7A935FF70}'],
               ['StdPicture?','{7BF80980-BF32-101A-8BBB-00AA00300CAB}','{7BF80980-BF32-101A-8BBB-00AA00300CAB}']];
    tests.forEach(function(t){
      var c=Memory.alloc(16); c.writeByteArray(g(t[1]));
      var i=Memory.alloc(16); i.writeByteArray(g(t[2]));
      var pp=Memory.alloc(4);
      var hr=CCI(c,ptr(0),1,i,pp);
      send2(t[0]+' hr=0x'+(hr>>>0).toString(16)+' obj='+pp.readPointer());
    });
  }catch(e){ send2('ERR '+e); }
}, 400);
send2('loaded');
