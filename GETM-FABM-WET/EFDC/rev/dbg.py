import ctypes, ctypes.wintypes as wt, time, sys, os, struct
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

k32 = ctypes.WinDLL('kernel32', use_last_error=True)
psapi = ctypes.WinDLL('psapi', use_last_error=True)

DEBUG_ONLY_THIS_PROCESS = 0x2
DBG_CONTINUE = 0x00010002
DBG_EXCEPTION_NOT_HANDLED = 0x80010001
EXCEPTION_DEBUG_EVENT = 1
CREATE_PROCESS_DEBUG_EVENT = 3
EXIT_PROCESS_DEBUG_EVENT = 5
LOAD_DLL_DEBUG_EVENT = 6
OUTPUT_DEBUG_STRING_EVENT = 8
BP_CODES = (0x80000003, 0x4000001F)     # x86 WOW64 breakpoint is 0x4000001F
SS_CODES = (0x80000004, 0x4000001E)

WOW64_CONTEXT_i386 = 0x00010000
WOW64_CONTEXT_CONTROL = WOW64_CONTEXT_i386 | 0x00000001
WOW64_CONTEXT_INTEGER = WOW64_CONTEXT_i386 | 0x00000002
WOW64_CONTEXT_FULL = WOW64_CONTEXT_CONTROL | WOW64_CONTEXT_INTEGER

# ---- 32-bit (WOW64) CONTEXT offsets ----
O_EIP, O_ESP, O_EFLAGS, O_EAX, O_ECX, O_EDX, O_EBX, O_ESI, O_EDI, O_EBP = 184, 196, 192, 176, 172, 168, 164, 160, 156, 180


class STARTUPINFOA(ctypes.Structure):
    _fields_ = [('cb', wt.DWORD), ('lpReserved', wt.LPSTR), ('lpDesktop', wt.LPSTR),
                ('lpTitle', wt.LPSTR), ('dwX', wt.DWORD), ('dwY', wt.DWORD),
                ('dwXSize', wt.DWORD), ('dwYSize', wt.DWORD), ('dwXCountChars', wt.DWORD),
                ('dwYCountChars', wt.DWORD), ('dwFillAttribute', wt.DWORD), ('dwFlags', wt.DWORD),
                ('wShowWindow', wt.WORD), ('cbReserved2', wt.WORD), ('lpReserved2', ctypes.c_void_p),
                ('hStdInput', wt.HANDLE), ('hStdOutput', wt.HANDLE), ('hStdError', wt.HANDLE)]


class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [('hProcess', wt.HANDLE), ('hThread', wt.HANDLE), ('dwProcessId', wt.DWORD),
                ('dwThreadId', wt.DWORD)]


class Dbg:
    def __init__(self, exe, logpath, timeout=60, mode='all'):
        self.exe = exe
        self.log = open(logpath, 'w', encoding='utf-8')
        self.timeout = timeout
        self.bps = {}
        self.hits = []
        self.threads = {}
        self.pid = None
        self.hProcess = None
        self.t0 = time.time()
        self.base = None
        self.mode = mode

    # ---------- io ----------
    def w(self, *a):
        line = ' '.join(str(x) for x in a)
        self.log.write(line + '\n')
        self.log.flush()
        try:
            print(line, flush=True)
        except Exception:
            pass

    def rp(self, addr, size):
        b = ctypes.create_string_buffer(size)
        n = ctypes.c_size_t(0)
        if not k32.ReadProcessMemory(self.hProcess, ctypes.c_void_p(addr), b, size, ctypes.byref(n)):
            return None
        return b.raw[:n.value]

    def u32(self, addr):
        d = self.rp(addr, 4)
        return struct.unpack('<I', d)[0] if d and len(d) == 4 else None

    def cstr(self, addr, n=240, wide=False):
        if not addr:
            return ''
        d = self.rp(addr, n * (2 if wide else 1))
        if not d:
            return '<unreadable>'
        try:
            if wide:
                return d.decode('utf-16le', 'replace').split('\x00')[0]
            return d.split(b'\x00')[0].decode('gbk', 'replace')
        except Exception:
            return repr(d[:40])

    # ---------- context ----------
    def tctx(self, tid):
        h = self.threads.get(tid)
        if h:
            return h
        h = k32.OpenThread(0x1F03FF, False, tid)
        self.threads[tid] = h
        return h

    def get_ctx(self, tid):
        h = self.tctx(tid)
        if not h:
            return None
        buf = ctypes.create_string_buffer(1024)
        struct.pack_into('<I', buf, 0, WOW64_CONTEXT_FULL)
        if not k32.Wow64GetThreadContext(ctypes.c_void_p(h), ctypes.byref(buf)):
            return None
        return buf

    def set_ctx(self, tid, buf):
        h = self.tctx(tid)
        return bool(h) and bool(k32.Wow64SetThreadContext(ctypes.c_void_p(h), ctypes.byref(buf)))

    # ---------- breakpoints ----------
    def bp(self, name, addr, extra=None):
        if addr in self.bps:
            return
        d = self.rp(addr, 1)
        if not d:
            self.w(f'!! cannot read bp site {name} {addr:#x}')
            return
        orig = d[0]
        b = ctypes.create_string_buffer(bytes([0xCC]))
        n = ctypes.c_size_t(0)
        ok = k32.WriteProcessMemory(self.hProcess, ctypes.c_void_p(addr), b, 1, ctypes.byref(n))
        self.bps[addr] = (name, orig, extra)
        self.w(f'BP {name:22s} @ {addr:#010x} orig={orig:#04x} write={"ok" if ok else "FAIL"}')

    # ---------- modules ----------
    def enum_modules(self):
        arr = (ctypes.c_void_p * 1024)()
        need = ctypes.c_size_t(0)
        ok = psapi.EnumProcessModulesEx(ctypes.c_void_p(self.hProcess), ctypes.byref(arr), ctypes.sizeof(arr),
                                        ctypes.byref(need), 3)  # LIST_MODULES_ALL
        mods = {}
        if not ok:
            self.w('EnumProcessModulesEx failed', ctypes.get_last_error())
            return mods
        cnt = need.value // ctypes.sizeof(ctypes.c_void_p)
        for i in range(cnt):
            hmod = arr[i]
            buf = ctypes.create_unicode_buffer(520)
            if psapi.GetModuleFileNameExW(ctypes.c_void_p(self.hProcess), ctypes.c_void_p(hmod), buf, 520):
                low = buf.value.lower()
                mods[low.split('\\')[-1]] = hmod
        return mods

    def arm_all(self):
        if self.mode == 'none':
            self.w('mode=none: no breakpoints armed')
            return
        mods = self.enum_modules()
        self.w('modules:', ', '.join(sorted(mods.keys())))
        if self.mode == 'api_only':
            table = {k: v for k, v in table.items()}
        table = {
            'oleaut32.dll': [('OleLoadPicture', 0x756e0), ('OleLoadPicturePath', 0x757d0),
                             ('OleCreatePictureIndirect', 0x377e0), ('OleLoadPictureFile', 0x75750)],
            'user32.dll': [('MessageBoxA', 0xaa090), ('MessageBoxW', 0xaa5b0),
                           ('MessageBoxIndirectA', 0xaa140), ('MessageBoxIndirectW', 0xaa280)],
            'msvbvm60.dll': [('rtcMsgBox', 0xee26a), ('__vbaError', 0xe6a99),
                             ('__vbaHresultCheckObj', 0x427c2), ('__vbaEnd', 0x427b8),
                             ('__vbaOnError', 0x1d872)],
            'gdi32.dll': [('GetObjectA', None)],
        }
        for dll, bplist in table.items():
            base = mods.get(dll)
            if not base:
                self.w('!! module missing', dll)
                continue
            for name, rva in bplist:
                if rva is None:
                    continue
                self.bp(name, base + rva, dll)

    # ---------- main loop ----------
    def run(self):
        si = STARTUPINFOA()
        si.cb = ctypes.sizeof(si)
        pi = PROCESS_INFORMATION()
        cmd = f'"{self.exe}"'
        os.chdir(os.path.dirname(self.exe))
        if not k32.CreateProcessW(None, ctypes.c_wchar_p(cmd), None, None, False,
                                  DEBUG_ONLY_THIS_PROCESS, None, None, ctypes.byref(si), ctypes.byref(pi)):
            self.w('CreateProcess failed', ctypes.get_last_error())
            return
        self.pid = pi.dwProcessId
        self.hProcess = pi.hProcess
        self.w(f'started pid={self.pid}')
        ev = ctypes.create_string_buffer(2048)
        while True:
            if not k32.WaitForDebugEvent(ctypes.byref(ev), 200):
                if time.time() - self.t0 > self.timeout:
                    self.w('timeout -> terminate')
                    k32.TerminateProcess(ctypes.c_void_p(self.hProcess), 0)
                    break
                continue
            raw = ev.raw
            code, pid, tid = struct.unpack_from('<III', raw, 0)
            status = DBG_CONTINUE
            try:
                if code == EXCEPTION_DEBUG_EVENT:
                    exc_code, _ = struct.unpack_from('<II', raw, 16)
                    exc_addr = struct.unpack_from('<Q', raw, 32)[0]
                    first = struct.unpack_from('<I', raw, 168)[0]
                    site = exc_addr & 0xFFFFFFFF
                    if exc_code in BP_CODES:
                        ctx = self.get_ctx(tid)
                        eip = struct.unpack_from('<I', ctx, O_EIP)[0] if ctx else None
                        hit = site if site in self.bps else (eip - 1 if eip else None)
                        if hit in self.bps:
                            name, orig, extra = self.bps.pop(hit)
                            b = ctypes.create_string_buffer(bytes([orig]))
                            n = ctypes.c_size_t(0)
                            k32.WriteProcessMemory(self.hProcess, ctypes.c_void_p(hit), b, 1, ctypes.byref(n))
                            if ctx:
                                struct.pack_into('<I', ctx, O_EIP, hit)
                                self.set_ctx(tid, ctx)
                                esp = struct.unpack_from('<I', ctx, O_ESP)[0]
                                a = [self.u32(esp + 4 * i) or 0 for i in range(1, 6)]
                                ret = self.u32(esp) or 0
                                t = time.time() - self.t0
                                self.w(f'HIT[{t:6.2f}] {name:22s} site={hit:#010x} ret={ret:#010x} '
                                       f'esp={esp:#010x} args=' + ','.join(f'{x:#x}' for x in a))
                                if name.startswith('MessageBox'):
                                    self.w('      text:', self.cstr(a[1]))
                                    self.w('      caption:', self.cstr(a[2]))
                                self.hits.append((t, name, hit, ret, a))
                                if name == 'exe_entry':
                                    self.arm_all()
                        else:
                            self.w(f'BP-exc at {site:#010x} eip={eip if eip is None else hex(eip)} not ours')
                    elif exc_code in SS_CODES:
                        pass
                    elif exc_code in (0xE06D7363, 0xE0434352):
                        pass
                    else:
                        self.w(f'EXC code={exc_code:#010x} addr={site:#010x} first={first}')
                        status = DBG_EXCEPTION_NOT_HANDLED   # let the app's own SEH see it
                elif code == CREATE_PROCESS_DEBUG_EVENT:
                    base = struct.unpack_from('<Q', raw, 40)[0]
                    self.base = base
                    self.w(f'CREATE_PROCESS base={base:#x}')
                    if self.mode != 'none':
                        self.bp('exe_entry', base + 0x51954)
                        if self.mode == 'all':
                            self.bp('CheckLicensing', base + 0x41C4C0)
                            self.bp('ShowExpiredForm?', base + 0x41F020)
                elif code == EXIT_PROCESS_DEBUG_EVENT:
                    ec = struct.unpack_from('<I', raw, 16)[0]
                    self.w(f'EXIT_PROCESS code={ec:#x}')
                    k32.ContinueDebugEvent(pid, tid, status)
                    break
            except Exception as e:
                self.w('loop error', repr(e))
            k32.ContinueDebugEvent(pid, tid, status)
        self.w(f'done hits={len(self.hits)} elapsed={time.time()-self.t0:.1f}s')


if __name__ == '__main__':
    exe = sys.argv[1]
    logp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dbg_log.txt')
    mode = sys.argv[3] if len(sys.argv) > 3 else 'all'
    d = Dbg(exe, logp, timeout=float(sys.argv[2]) if len(sys.argv) > 2 else 50, mode=mode)
    try:
        d.run()
    finally:
        d.log.close()

