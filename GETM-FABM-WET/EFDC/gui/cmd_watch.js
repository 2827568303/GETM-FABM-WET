// Log WM_COMMAND notifications (32-bit process) so toolbar button IDs can be identified.
const user32 = Process.getModuleByName('user32.dll');
const pDispatch = user32.getExportByName('DispatchMessageW');
let n = 0;

Interceptor.attach(pDispatch, {
    onEnter: function (args) {
        try {
            const msg = args[0];
            const message = msg.add(4).readU32();
            if (message === 0x0111) {
                const wParam = msg.add(8).readU32();
                const lParam = msg.add(12).readU32();
                n++;
                console.log('WM_COMMAND id=' + wParam + ' ctrl=0x' + lParam.toString(16));
            }
        } catch (e) { }
    }
});
console.log('[*] dispatch hook ready');
