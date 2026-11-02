# -*- coding: utf-8 -*-
"""Try to decrypt the DSILIC config URL values with the key candidate found in the DLL."""
import base64
import hashlib
import itertools
import zlib

from Crypto.Cipher import AES, DES3, ARC4
from Crypto.Util.Padding import unpad

CIPHERS = {
    "timeUrl": "i06+QAtQZc6mFGPVi22ZbDpXt6QQY4yhL6FcGB+aIQzZRCbeEB3s1LT/RxWybZt3sRoa31dBiWD2lSJTEFroNg==",
    "proxyUrl": "n4Frk0+BKKD42A3E6n+WSW1BzisD1+asJPR4zD8Irt3Hxt9UOwDMWRZIMUlMBTsK",
    "demoUrl": "n4Frk0+BKKD42A3E6n+WSW6ZT3t2sw+PhniPs+8OL4HOVKJ+HNNpcT3IsVojO7Dl",
}

SECRETS = ["dsi@2016#lic!", "dsi@2016#lic", "dsi@2016", "dsi@efdc2015", "dsi@efdc2015#lic!"]


def key_variants(secret):
    b = secret.encode()
    out = {}
    out["md5"] = hashlib.md5(b).digest()
    out["sha1-16"] = hashlib.sha1(b).digest()[:16]
    out["sha256"] = hashlib.sha256(b).digest()
    out["sha256-16"] = hashlib.sha256(b).digest()[:16]
    out["sha256-24"] = hashlib.sha256(b).digest()[:24]
    out["raw16"] = (b + b"\0" * 16)[:16]
    out["raw24"] = (b + b"\0" * 24)[:24]
    out["raw32"] = (b + b"\0" * 32)[:32]
    out["raw-trunc"] = b[:16] if len(b) >= 16 else (b + b"\0" * 16)[:16]
    out["md5hex16"] = hashlib.md5(b).hexdigest().encode()[:16]
    return out


def looks_good(data):
    if not data:
        return False
    try:
        t = data.decode("utf-8", "ignore")
    except Exception:
        return False
    return "http" in t or "php" in t or "/" in t


def try_inflate(data):
    for wbits in (15, -15, 31, 47):
        try:
            return zlib.decompress(data, wbits)
        except Exception:
            pass
    return None


results = []
for name, b64 in CIPHERS.items():
    raw = base64.b64decode(b64 + "=" * (-len(b64) % 4))
    print("%-9s cipher bytes = %d" % (name, len(raw)))
    for secret in SECRETS:
        for kname, key in key_variants(secret).items():
            if len(key) not in (16, 24, 32):
                continue
            for ivname, iv in (("zero", b"\0" * 16), ("key", (key + b"\0" * 16)[:16]),
                               ("md5key", hashlib.md5(key).digest())):
                for mode_name, factory in (("CBC", lambda: AES.new(key, AES.MODE_CBC, iv)),
                                           ("ECB", lambda: AES.new(key, AES.MODE_ECB))):
                    try:
                        pt = factory().decrypt(raw)
                    except Exception:
                        continue
                    candidates = [pt]
                    try:
                        candidates.append(unpad(pt, 16))
                    except Exception:
                        pass
                    inf = try_inflate(pt)
                    if inf:
                        candidates.append(inf)
                    for c in candidates:
                        if looks_good(c):
                            txt = c.decode("utf-8", "ignore")
                            results.append((name, secret, kname, mode_name, ivname, txt))
                            print("  HIT %-9s %-14s %-10s %-5s %-6s -> %r" % (name, secret, kname, mode_name, ivname, txt[:80]))
                            break

print("----")
print("hits:", len(results))
for r in results[:12]:
    print(r)
