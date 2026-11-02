import re, io

SRC = r"C:\EFDC84_LIC\DSILIC1.dll.vendor"
b = open(SRC, "rb").read()
out = []

needle = "www.eems-analytics.info"
u = needle.encode("utf-16-le")
for m in re.finditer(re.escape(u), b):
    start = m.start()
    # 向前后各取 200 字节，按 UTF-16 解码后找完整 URL
    seg = b[max(0, start - 120):start + 260]
    try:
        txt = seg.decode("utf-16-le", "replace")
    except Exception as e:
        txt = "<decode err>"
    out.append("hit @0x%X\n  raw: %r\n" % (start, txt))

# 也找 https:// 前缀的 UTF-16
for m in list(re.finditer(re.escape("https://".encode("utf-16-le")), b))[:10]:
    out.append("https:// @0x%X\n  %r\n" % (m.start(), b[m.start():m.start()+240].decode("utf-16-le", "replace")))

io.open(r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\url_dump.txt", "w", encoding="utf-8").write("\n".join(out))
print("wrote", len(out), "entries")
