'use strict';
function send2(s) { send(s); }
var trace = [];
var started = false;

setTimeout(function () {
    try {
        var ths = Process.enumerateThreads();
        var main = ths[0];
        send2('following thread ' + main.id);
        Stalker.follow(main.id, {
            transform: function (iterator) {
                var ins;
                while ((ins = iterator.next()) !== null) {
                    try {
                        var a = ins.address;
                        var v = a.toUInt32 ? a.toUInt32() : parseInt(a.toString(), 16);
                        if (v >= 0x401000 && v < 0x1620000) {
                            if (trace.length < 4000) trace.push(v.toString(16));
                        }
                    } catch (e) { }
                }
            }
        });
        started = true;
    } catch (e) { send2('STALKER ERR ' + e); }
}, 3800);

setTimeout(function () {
    if (!started) { send2('not started'); return; }
    try { Stalker.unfollow(); Stalker.flush(); } catch (e) { }
    send2('trace len=' + trace.length);
    send2('TRACE ' + trace.join(','));
}, 5200);
send2('loaded');

