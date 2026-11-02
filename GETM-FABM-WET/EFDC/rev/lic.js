'use strict';
function send2(s) { send(s); }
function gs(p) {
    try {
        var b = new Uint8Array(p.readByteArray(16));
        function h(x) { return ('0' + x.toString(16)).slice(-2); }
        var d1 = (b[3] << 24 | b[2] << 16 | b[1] << 8 | b[0]) >>> 0, d2 = (b[5] << 8 | b[4]), d3 = (b[7] << 8 | b[6]), s = '';
        for (var i = 8; i < 16; i++) s += h(b[i]);
        return ('00000000' + d1.toString(16)).slice(-8) + '-' + ('0000' + d2.toString(16)).slice(-4) + '-' +
            ('0000' + d3.toString(16)).slice(-4) + '-' + s.substr(0, 4) + '-' + s.substr(4);
    } catch (e) { return '?'; }
}
function wstr(p) { try { return p.isNull() ? '' : p.readUtf16String(); } catch (e) { return '<bad>'; } }
var IMAGELIST = '2c247f23-8591-11d1-b16a-00c0f0283628';
var hooked = {};

setTimeout(function () {
    try {
        var ole32 = Process.findModuleByName('ole32.dll');
        var p = ole32.findExportByName('CoGetClassObject');
        Interceptor.attach(p, {
            onEnter: function (a) {
                this.c = gs(a[0]);
                this.ppv = a[4];
            },
            onLeave: function (r) {
                var hr = r.toInt32() >>> 0;
                if (this.c !== IMAGELIST || hr !== 0) return;
                try {
                    var cf = this.ppv.readPointer();
                    send2('GOT FACTORY ' + cf);
                    var vt = cf.readPointer();
                    [3, 4].forEach(function (idx) {
                        var fn = vt.add(idx * 4).readPointer();
                        if (hooked[fn.toString()]) return;
                        hooked[fn.toString()] = 1;
                        Interceptor.attach(fn, {
                            onEnter: function (a) {
                                this.what = 'IClassFactory' + (idx === 4 ? '2::CreateInstanceLic' : '::CreateInstance');
                                this.lic = idx === 4 ? wstr(a[3]) : '';
                                this.ppv = idx === 4 ? a[4] : a[3];
                            },
                            onLeave: function (r) {
                                send2(this.what + ' lic=' + JSON.stringify(this.lic) + ' hr=0x' + ((r.toInt32() >>> 0).toString(16)) +
                                    ' obj=' + (this.ppv ? this.ppv.readPointer() : '?'));
                            }
                        });
                        send2('hooked vtable[' + idx + '] @' + fn);
                    });
                } catch (e) { send2('factory hook err ' + e); }
            }
        });
        send2('hooked CoGetClassObject');
    } catch (e) { send2('ERR ' + e); }
}, 300);
send2('loaded');
