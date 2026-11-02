'use strict';
function emit(s){ send(s); }
var IID=[0x81,0x09,0xF8,0x7B,0x32,0xBF,0x1A,0x10,0x8B,0xBB,0x00,0xAA,0x00,0x30,0x0C,0xAB];
setTimeout(function(){
  try{
    var oa=Process.findModuleByName('oleaut32.dll');
    var gdi=Process.findModuleByName('gdi32.dll');
    var CreateBitmap=new NativeFunction(gdi.findExportByName('CreateBitmap'),'pointer',['int','int','uint','uint','pointer']);
    var OleCreate=new NativeFunction(oa.findExportByName('OleCreatePictureIndirect'),'uint',['pointer','pointer','int','pointer']);
    var iid=Memory.alloc(16); iid.writeByteArray(new Uint8Array(IID));
    Interceptor.attach(oa.findExportByName('OleLoadPictureEx'),{
      onEnter:function(a){ this.ppv=a[7]; },
      onLeave:function(r){
        if((r.toInt32()>>>0)===0) return;
        try{ var hbmp=CreateBitmap(2,2,1,1,ptr(0));
          var desc=Memory.alloc(16); desc.writeU32(16); desc.add(4).writeU32(1); desc.add(8).writePointer(hbmp); desc.add(12).writePointer(ptr(0));
          if((OleCreate(desc,iid,1,this.ppv)>>>0)===0) r.replace(ptr(0)); }catch(e){}
      }
    });
    emit('picfix ready');
  }catch(e){ emit('ERR '+e); }
}, 200);

var counts = {};
var label = {};
setTimeout(function(){
  emit('sampling start t=12s');
  var iv = setInterval(function(){
    try{
      var ts = Process.enumerateThreads();
      for (var i=0;i<ts.length;i++){
        var k = ts[i].id + '|' + ts[i].context.pc.toString();
        counts[k] = (counts[k]||0)+1;
      }
    }catch(e){}
  }, 2);
  setTimeout(function(){
    clearInterval(iv);
    var arr = Object.keys(counts).map(function(k){return [k,counts[k]];});
    arr.sort(function(a,b){return b[1]-a[1];});
    var lines = [];
    for (var i=0;i<Math.min(50,arr.length);i++){
      var p = arr[i][0].split('|');
      var pc = ptr(p[1]);
      var m = Process.findModuleByAddress(pc);
      var loc = m ? (m.name + '+0x' + pc.sub(m.base).toString(16)) : p[1];
      lines.push('th' + p[0] + '  ' + loc + '  x' + arr[i][1]);
    }
    emit('TOP\n' + lines.join('\n'));
    try{
      var mts = Process.enumerateThreads();
      mts.forEach(function(t){
        var bts = Thread.backtrace(t.context, Backtracer.FUZZY).slice(0,18).map(function(a){
          var m = Process.findModuleByAddress(a);
          return m ? (m.name+'+0x'+a.sub(m.base).toString(16)) : a.toString();
        });
        emit('BT th'+t.id+' pc='+t.context.pc+' :: '+bts.join(' <- '));
      });
    }catch(e){ emit('bterr '+e); }
  }, 15000);
}, 12000);
emit('loaded');
