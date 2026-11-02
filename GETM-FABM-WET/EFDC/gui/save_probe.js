// Broad write detector: CreateFileW(write), WritePrivateProfileStringW, WriteFile attribution.
const user32 = Process.getModuleByName('user32.dll');
const kernel32 = Process.getModuleByName('kernel32.dll');
const pCreateFileW = kernel32.getExportByName('CreateFileW');
const pWriteFile = kernel32.getExportByName('WriteFile');
const pWriteIni = kernel32.getExportByName('WritePrivateProfileStringW');
const paths = {};

function hookCmd(fn) {
    try {
        Interceptor.attach(user32.getExportByName(fn), {
            onEnter: function (args) {
                try {
                    const msg = (fn === 'DispatchMessageW') ? args[0].add(4).readU32() : (args[1].toInt32() & 0xffff);
                    if (msg === 0x0111) {
                        let id;
                        if (fn === 'DispatchMessageW') id = args[0].add(8).readU32() & 0xffff;
                        else id = args[2].toInt32() & 0xffff;
                        console.log(fn + ' CMD id=' + id);
                    }
                } catch (e) { }
            }
        });
    } catch (e) { }
}
hookCmd('DispatchMessageW');
hookCmd('SendMessageW');

Interceptor.attach(pCreateFileW, {
    onEnter: function (args) {
        try {
            const path = args[0].isNull() ? '' : (args[0].readUtf16String() || '');
            const access = args[1].toInt32();
            const wantWrite = (access & 0x40000000) !== 0 || (access & 0x2) !== 0 || (access & 0x4) !== 0;
            if (wantWrite) console.log('OPEN-W ' + path);
            this.path = path;
        } catch (e) { this.path = ''; }
    },
    onLeave: function (ret) {
        try { if (this.path && !ret.isNull() && ret.toInt32() !== -1) paths[ret.toString()] = this.path; } catch (e) { }
    }
});

Interceptor.attach(pWriteFile, {
    onEnter: function (args) {
        try {
            const n = args[2].toInt32();
            const p = paths[args[0].toString()] || '';
            if (p && n > 0) console.log('WRITE ' + n + ' -> ' + p);
        } catch (e) { }
    }
});

Interceptor.attach(pWriteIni, {
    onEnter: function (args) {
        try {
            const sec = args[0].isNull() ? '' : (args[0].readUtf16String() || '');
            const key = args[1].isNull() ? '' : (args[1].readUtf16String() || '');
            const file = args[3].isNull() ? '' : (args[3].readUtf16String() || '');
            console.log('INI ' + file + ' [' + sec + '] ' + key);
        } catch (e) { }
    }
});

console.log('[*] hooks ready');
