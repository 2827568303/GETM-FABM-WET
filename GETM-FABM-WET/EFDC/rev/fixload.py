p='loadhook.js'; s=open(p,encoding='utf-8').read()
s=s.replace("""                var psIid = Memory.alloc(16);
                psIid.writeByteArray(new Uint8Array([0x09, 0x01, 0, 0, 0, 0, 0, 0, 0xC0, 0, 0, 0, 0, 0, 0, 0x46]));
                var pps = Memory.alloc(4);
                var hr2 = QI(obj, psIid, pps);
                var ps = pps.readPointer();
                send2('QI(IPersistStream) hr=0x' + (hr2 >>> 0).toString(16) + ' ps=' + ps);
                if (ps.isNull()) return;
                done = true;
                var pvt = ps.readPointer();
                for (var i = 3; i <= 7; i++) {
                    var f = pvt.add(i * 4).readPointer();
                    send2('PS slot ' + i + ' rva=' + f.sub(mod.base).toString(16));
                }
                var load = pvt.add(5 * 4).readPointer();""","""                var cands = [
                  ['IPersistStreamInit', [0x80,0x23,0xD5,0x7F,0x07,0x4E,0x1B,0x10,0xAE,0x2D,0x08,0x00,0x2B,0x2E,0xC7,0x13], 5],
                  ['IPersistPropertyBag', [0x60,0x4F,0xD8,0x37,0xCB,0x42,0xCE,0x11,0x81,0x35,0x00,0xAA,0x00,0x4B,0xB8,0x51], 5],
                  ['IPersistStream', [0x09,0x01,0,0,0,0,0,0,0xC0,0,0,0,0,0,0,0x46], 5],
                  ['IPersistStorage', [0x0A,0x01,0,0,0,0,0,0,0xC0,0,0,0,0,0,0,0x46], 6]
                ];
                var ps = ptr(0), loadIdx = 5, which = '';
                for (var ci = 0; ci < cands.length; ci++) {
                  var ii = Memory.alloc(16); ii.writeByteArray(new Uint8Array(cands[ci][1]));
                  var p2 = Memory.alloc(4);
                  var h2 = QI(obj, ii, p2);
                  send2('QI(' + cands[ci][0] + ') hr=0x' + (h2 >>> 0).toString(16) + ' p=' + p2.readPointer());
                  if ((h2 >>> 0) === 0) { ps = p2.readPointer(); loadIdx = cands[ci][2]; which = cands[ci][0]; break; }
                }
                if (ps.isNull()) return;
                done = true;
                var pvt = ps.readPointer();
                var load = pvt.add(loadIdx * 4).readPointer();
                send2('using ' + which + ' load rva=' + load.sub(mod.base).toString(16));""")
open(p,'w',encoding='utf-8').write(s)
print('ok')
