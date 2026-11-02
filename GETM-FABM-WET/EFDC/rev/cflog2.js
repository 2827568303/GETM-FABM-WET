'use strict';
function send2(s) { send(s); }
function wstr(p) { try { return p.isNull() ? '' : p.readUtf16String(); } catch (e) { return '<bad>'; } }
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
var IMAGELIST = '2c247f23-8591-11d1-b16a-00c0f0283628';
var hooked = {};
setTimeout(function () {
    var ole32 = Process.findModuleByName('ole32.dll');
    Interceptor.attach(ole32.findExportByName('CoGetClassObject'), {
        onEnter: function (a) { this.c = gs(a[0]); this.ppv = a[4]; },
        onLeave: function (r) {
            if (this.c !== IMAGELIST) return;
            var hr = r.toInt32() >>> 0;
            try {
                var cf = this.ppv.readPointer();
                send2('CoGetClassObject(ImageList) hr=0x' + hr.toString(16) + ' cf=' + cf);
                if (hr !== 0 || cf.isNull() || hooked[cf.toString()]) return;
                hooked[cf.toString()] = 1;
                var cvt = cf.readPointer();
                [3, 7].forEach(function (idx) {
                    var fn = cvt.add(idx * 4).readPointer();
                    Interceptor.attach(fn, {
                        onEnter: function (a) {
                            this.ppv = idx === 7 ? a[5] : a[3];
                            this.key = idx === 7 ? wstr(a[4]) : '';
                            this.riid = gs(idx === 7 ? a[3] : a[2]);
                        },
                        onLeave: function (r2) {
                            var o = '?';
                            try { o = this.ppv.readPointer(); } catch (e) { }
                            send2('  CF' + idx + ' riid=' + this.riid + ' key=' + JSON.stringify(this.key) +
                                ' hr=0x' + ((r2.toInt32() >>> 0).toString(16)) + ' obj=' + o);
                        }
                    });
                });
                send2('  hooked ImageList factory slots');
            } catch (e) { send2('ERR ' + e); }
        }
    });
    send2('hooked CoGetClassObject');
}, 300);
send2('loaded');
