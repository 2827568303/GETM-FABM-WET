// Trace who opens .inp/.EE files with write access (stack -> caller VA).
const kernel32 = Process.getModuleByName('kernel32.dll');
const pCreateFileW = kernel32.getExportByName('CreateFileW');
const mod = Process.getModuleByName('EFDC_Explorer8.4.exe');

Interceptor.attach(pCreateFileW, {
    onEnter: function (args) {
        try {
            const path = args[0].isNull() ? '' : (args[0].readUtf16String() || '');
            const access = args[1].toInt32();
            const write = (access & 0x40000000) !== 0 || (access & 0x2) !== 0 || (access & 0x4) !== 0;
            if (!write || !/\.inp$|\.EE$|\.INP$/i.test(path)) return;
            const bt = Thread.backtrace(this.context, Backtracer.FUZZY).slice(0, 6).map(function (a) {
                const m = Process.findModuleByAddress(a);
                if (!m) return a.toString();
                if (m.base.equals(mod.base)) return 'EFDC+0x' + a.sub(m.base).toString(16);
                return m.name + '+0x' + a.sub(m.base).toString(16);
            });
            console.log('OPEN-W ' + path + ' acc=0x' + access.toString(16));
            console.log('   ' + bt.join('\n   '));
        } catch (e) { }
    }
});
console.log('[*] trace ready');
