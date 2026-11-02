p='mainshow2.js'; s=open(p,encoding='utf-8').read()
s=s.replace("""    var pm=u.findExportByName('PeekMessageW');
    Interceptor.attach(pm,{""","""    ['PeekMessageW','PeekMessageA','GetMessageW','GetMessageA','DispatchMessageA','DispatchMessageW'].forEach(function(fname){
    var pm=u.findExportByName(fname); if(!pm) return;
    Interceptor.attach(pm,{""")
s=s.replace("""      }
    });
    emit('ready');""","""      }
    });
    });
    emit('ready');""")
open(p,'w',encoding='utf-8').write(s)
print('ok')
