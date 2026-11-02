'use strict';
var t0 = Date.now();
function ts(){ var d = Date.now()-t0; return d.toString().padStart(6,' '); }
function emit(s){ send(ts()+' '+s); }
function mod(addr){ try{ var m = Process.findModuleByAddress(addr); return m? (m.name+'+0x'+addr.sub(m.base).toString(16)) : addr.toString(); }catch(e){ return '?'; } }

// ---- picture fix (needed to pass Error 481) ----
var IID=[0x81,0x09,0xF8,0x7B,0x32,0xBF,0x1A,0x10,0x8B,0xBB,0x00,0xAA,0x00,0x30,0x0C,0xAB];
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
  emit('picfix installed');
}catch(e){ emit('picfix ERR '+e); }

function hook(modname, name, onEnter, onLeave){
  try{
    var m = Process.findModuleByName(modname);
    if(!m) return false;
    var a = m.findExportByName(name);
    if(!a) return false;
    Interceptor.attach(a, { onEnter: onEnter, onLeave: onLeave });
    return true;
  }catch(e){ emit('hookfail '+modname+'!'+name+' '+e); return false; }
}
function wstr(p){ try{ return p.readUtf16String()||''; }catch(e){ return ''; } }

var N = {u32:'user32.dll', k32:'kernel32.dll', adv:'advapi32.dll', ws2:'ws2_32.dll', winhttp:'winhttp.dll', wininet:'wininet.dll', ole:'ole32.dll', shl:'shell32.dll'};

hook(N.u32,'MessageBoxW',function(a){ emit('MessageBoxW "'+wstr(a[1])+'" from '+mod(this.returnAddress)); });
hook(N.u32,'CreateWindowExW',function(a){
  var cls = wstr(a[1]); var nm = wstr(a[2]);
  if(cls.indexOf('Thunder')>=0 || cls==='#32770' || cls.indexOf('MSVB')>=0)
    emit('CreateWindowExW cls='+cls+' title="'+nm+'" style=0x'+(a[3].toInt32()>>>0).toString(16)+' from '+mod(this.returnAddress));
});
hook(N.u32,'ShowWindow',function(a){ emit('ShowWindow hwnd='+a[0]+' cmd='+a[1]+' from '+mod(this.returnAddress)); });
hook(N.u32,'SetTimer',null,null);
hook(N.k32,'Sleep',function(a){ var ms=a[0].toInt32(); if(ms>50) emit('Sleep '+ms+' from '+mod(this.returnAddress)); });
hook(N.k32,'CreateProcessW',function(a){ emit('CreateProcessW cmd="'+wstr(a[1])+'" from '+mod(this.returnAddress)); });
hook(N.k32,'CreateFileW',function(a){ var p=wstr(a[0]); if(p.indexOf('DSI')>=0||p.indexOf('EEMS')>=0||p.indexOf('EFDC')>=0||p.indexOf('lic')>=0) emit('CreateFileW "'+p+'" from '+mod(this.returnAddress)); });
hook(N.adv,'RegCreateKeyExW',function(a){ emit('RegCreateKeyExW "'+wstr(a[1])+'" from '+mod(this.returnAddress)); });
hook(N.winhttp,'WinHttpOpen',function(a){ emit('WinHttpOpen'); });
hook(N.winhttp,'WinHttpSendRequest',function(a){ emit('WinHttpSendRequest'); });
hook(N.wininet,'InternetOpenW',function(a){ emit('InternetOpenW'); });
hook(N.ws2,'WSAConnect',function(a){ emit('WSAConnect'); });
hook(N.ws2,'getaddrinfo',function(a){ emit('getaddrinfo "'+wstr(a[0])+'"'); });
hook(N.ws2,'gethostbyname',function(a){ emit('gethostbyname "'+wstr(a[0])+'"'); });
hook(N.ole,'OleLoadPictureEx',function(a){ emit('OleLoadPictureEx size='+a[1].toInt32()); });
hook(N.shl,'ShellExecuteW',function(a){ emit('ShellExecuteW "'+wstr(a[2])+'" "'+wstr(a[3])+'"'); });
hook('msvbvm60.dll','__vbaFileOpen',function(a){ emit('vbaFileOpen "'+wstr(a[0])+'"'); });
hook('msvbvm60.dll','rtcShell',function(a){ emit('rtcShell "'+wstr(a[0])+'"'); });

// ---- PC sampling via RPC ----
rpc.exports = {
  snapshot: function(){
    var out = [];
    try{
      var ts2 = Process.enumerateThreads();
      for (var i=0;i<ts2.length;i++){
        var t = ts2[i];
        var bt = [];
        try{ bt = Thread.backtrace(t.context, Backtracer.FUZZY).slice(0,10).map(mod); }catch(e){}
        out.push({id:t.id, pc:mod(t.context.pc), bt:bt});
      }
    }catch(e){ out.push({err:''+e}); }
    return out;
  }
};
emit('trace hooks installed');
