'use strict';
var t0 = Date.now();
function ts(){ return (Date.now()-t0).toString().padStart(6,' '); }
function emit(s){ send(ts()+' '+s); }
function mod(a){ try{ var m=Process.findModuleByAddress(a); return m?(m.name+'+0x'+a.sub(m.base).toString(16)):a.toString(); }catch(e){ return '?'; } }
function wstr(p){ try{ return p.readUtf16String()||''; }catch(e){ return ''; } }
function astr(p){ try{ return p.readAnsiString()||''; }catch(e){ return ''; } }

// picture fix
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
  emit('picfix ok');
}catch(e){ emit('picfix ERR '+e); }

function find(name){ var m=Process.findModuleByName('kernel32.dll'); return m.findExportByName(name); }
var pCreateFileW=find('CreateFileW'), pWriteFile=find('WriteFile'), pCloseHandle=find('CloseHandle');
var pGetLastError=find('GetLastError');
var GetLastError=new NativeFunction(pGetLastError,'uint',[]);
var tracked = {};   // handle string -> path

Interceptor.attach(pCreateFileW, {
  onEnter:function(a){ this.path = wstr(a[0]); this.want = /DSI|EEMS|EFDC|\.log|\.lic|\.bmp|\.ini|\.mdb/i.test(this.path); },
  onLeave:function(r){
    if(!this.want || !this.path) return;
    var h = r.toInt32()>>>0;
    emit('CreateFileW "'+this.path+'" h='+h+' err='+GetLastError());
    if (h !== 0xFFFFFFFF) tracked[h] = this.path;
  }
});
Interceptor.attach(pWriteFile, {
  onEnter:function(a){
    var h = a[0].toInt32()>>>0;
    var p = tracked[h];
    if(!p) return;
    var n = a[2].toInt32();
    if(n<=0 || n>4096) return;
    try{
      var buf = a[1].readByteArray(n);
      var u8 = new Uint8Array(buf);
      var printable = 0;
      for (var i=0;i<u8.length;i++){ var c=u8[i]; if(c>=9&&c<127) printable++; }
      if (printable/u8.length > 0.85) emit('WRITE['+p.split('\\').pop()+'] '+String.fromCharCode.apply(null,u8).replace(/\r/g,'').replace(/\n/g,' | '));
    }catch(e){}
  }
});
Interceptor.attach(pCloseHandle, {
  onEnter:function(a){ var h=a[0].toInt32()>>>0; if(tracked[h]){ emit('CloseHandle '+tracked[h]); delete tracked[h]; } }
});

// exception handler: capture crash
try{
  Process.setExceptionHandler(function(details){
    emit('!!! EXCEPTION '+details.type+' at '+details.address+' thread='+details.threadId);
    try{ var ctx=details.context;
      emit('   eip='+ctx.pc+' esp='+ctx.sp+' eax='+ctx.rax+' ebx='+ctx.rbx+' ecx='+ctx.rcx+' edx='+ctx.rdx+' esi='+ctx.rsi+' edi='+ctx.rdi+' ebp='+ctx.rbp);
      var bts = Thread.backtrace(ctx, Backtracer.FUZZY).slice(0,16).map(mod);
      emit('   bt: '+bts.join(' <- '));
    }catch(e){ emit('   ctxerr '+e); }
    return false;
  });
  emit('exhandler ok');
}catch(e){ emit('exhandler ERR '+e); }
emit('ready');
