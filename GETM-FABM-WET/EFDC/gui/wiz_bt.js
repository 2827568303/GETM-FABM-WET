// Log the call stack that makes the Activation Wizard / Sign-in form visible.
const user32 = Process.getModuleByName('user32.dll');
const pShow = user32.getExportByName('ShowWindow');
const pGetText = user32.getExportByName('GetWindowTextW');
const GetWindowTextW = new NativeFunction(pGetText, 'int', ['pointer', 'pointer', 'int']);

function title(h) {
    const buf = Memory.alloc(1024);
    GetWindowTextW(h, buf, 512);
    try { return buf.readUtf16String() || ''; } catch (e) { return ''; }
}

function bt(ctx, n) {
    return Thread.backtrace(ctx, Backtracer.FUZZY).slice(0, n).map(function (a) {
        const m = Process.findModuleByAddress(a);
        return m ? (m.name + '+0x' + a.sub(m.base).toString(16)) : a.toString();
    });
}

Interceptor.attach(pShow, {
    onEnter: function (args) {
        this.h = args[0];
        this.ctx = this.context;
    },
    onLeave: function (ret) {
        try {
            const t = title(this.h);
            if (t && (t.indexOf('Activation') >= 0 || t.indexOf('Sign in') >= 0 || t.indexOf('Wizard') >= 0)) {
                console.log('[SHOW] ' + JSON.stringify(t) + ' hwnd=' + this.h + ' cmd=' + ret);
                console.log('  ' + bt(this.ctx, 12).join('\n  '));
            }
        } catch (e) { console.log('err ' + e); }
    }
});
console.log('[*] hook installed');
