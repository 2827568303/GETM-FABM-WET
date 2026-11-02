// Read the license/restriction globals from a running EFDC_Explorer8.4 process.
const mod = Process.getModuleByName('EFDC_Explorer8.4.exe');
function u16(va) { try { return mod.base.add(va - 0x400000).readU16(); } catch (e) { return 'ERR ' + e; } }
function u32(va) { try { return mod.base.add(va - 0x400000).readU32(); } catch (e) { return 'ERR ' + e; } }
function str(va) {
    try {
        const p = mod.base.add(va - 0x400000).readPointer();
        return p.isNull() ? null : p.readUtf16String();
    } catch (e) { return 'ERR ' + e; }
}
console.log(JSON.stringify({
    base: mod.base.toString(),
    licType_16204a0: u16(0x16204a0),
    demoFlagA_16203f4: u16(0x16203f4),
    demoFlagB_16203f6: u16(0x16203f6),
    isActivated_16204c4: u16(0x16204c4),
    featureName_16203fc: str(0x16203fc),
    licLimitText_162049c: str(0x162049c),
    prod_1620444: str(0x1620444),
    cells_16225c0: u32(0x16225c0)
}, null, 1));
