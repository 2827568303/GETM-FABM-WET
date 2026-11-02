'use strict';
var T0 = Date.now();
function t() { return ((Date.now() - T0) / 1000).toFixed(2); }
function send2(s) { send(s); }
function bp(addr, name) {
    try {
        Interceptor.attach(ptr(addr), function () {
            send2('[' + t() + '] ' + name + ' @' + addr);
        });
    } catch (e) { send2('!! bp fail ' + name + ' ' + e); }
}
var V = 0x400000;   // exe base
bp(0x81C5AC, 'body-start');
bp(0x81C68F, 'step2-read-license');
bp(0x81C73C, 'GetMachineId');
bp(0x81C87E, 'IsActivated-chk');
bp(0x81C903, 'step6');
bp(0x81C928, '6.1-activated');
bp(0x81C98B, '6.1.1-time');
bp(0x81C9B3, '6.1.2-features');
bp(0x81CA1F, '6.1.3-FNO');
bp(0x81CA50, '6.1.4-licfile');
bp(0x81CA5E, 'after-licfile');
bp(0x81CB00, 'versiondate-a');
bp(0x81CBE8, 'versiondate-sorry');
bp(0x81CD73, 'feature-cmp');
bp(0x81CD95, 'CALL-End');
bp(0x81CD9B, 'SUCCESS-81bba0');
bp(0x81CDA0, 'SUCCESS-828f50');
bp(0x81CDB6, 'ShowExpiredForm');
bp(0x81CE14, 'ERRMSG-block');
bp(0x81CE93, 'ERRMSG-msgbox');
bp(0x81D03E, 'exitproc');
bp(0x81D0D3, 'epilogue');
bp(0x828F50, 'form-init');
bp(0x156ACC0, 'title-form');
send2('script loaded');
