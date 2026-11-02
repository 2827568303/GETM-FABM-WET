'use strict';
function send2(s) { send(s); }
setTimeout(function () {
    try {
        var m = Process.findModuleByName('MSVBVM60.DLL');
        var fn = m.base.add(0x1D740);
        send2('wrapper at ' + fn);
        Interceptor.attach(fn, {
            onEnter: function (a) {
                var vals = [];
                this.args = [];
                for (var i = 8; i <= 0x24; i += 4) {
                    try {
                        var v = this.context.ebp.add(i).readU32();
                        this.args.push({ off: i, addr: v });
                        vals.push('[' + i.toString(16) + ']=' + v.toString(16));
                    } catch (e) { vals.push('[' + i.toString(16) + ']=?'); }
                }
                send2('wrapper enter: ' + vals.join(' '));
                this.pre = this.args.map(function (x) {
                    try { return ptr(x.addr).readU32(); } catch (e) { return null; }
                });
            },
            onLeave: function (r) {
                var hr = r.toInt32() >>> 0;
                var out = [];
                for (var i = 0; i < this.args.length; i++) {
                    var a = this.args[i];
                    var now = null;
                    try { now = ptr(a.addr).readU32(); } catch (e) { }
                    if (now !== this.pre[i]) out.push('[+' + a.off.toString(16) + '] ' + (this.pre[i] === null ? '?' : this.pre[i].toString(16)) + '->' + (now === null ? '?' : now.toString(16)));
                }
                send2('wrapper leave hr=0x' + hr.toString(16) + '  changed: ' + out.join(' | '));
            }
        });
        send2('hooked wrapper');
    } catch (e) { send2('ERR ' + e); }
}, 200);
send2('loaded');
