import io, os, shutil, sys

SRC = r"C:\EFDC84_LIC\DSILIC1.dll.vendor"
DSTS = [
    r"C:\EFDC84_LIC\DSILIC1.dll",
    r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\DSILIC1.dll",
]

OLD = "https://www.eems-analytics.info/wp-json/v2/eemsdemo/"
NEW = "http://127.0.0.1:8080/wp-json/v2/eemsdemo/" + "/" * (len(OLD) - len("http://127.0.0.1:8080/wp-json/v2/eemsdemo/"))
assert len(NEW) == len(OLD), (len(NEW), len(OLD))

b = bytearray(open(SRC, "rb").read())
pat = OLD.encode("utf-16-le")
rep = NEW.encode("utf-16-le")
n = 0
i = 0
while True:
    j = b.find(pat, i)
    if j < 0:
        break
    b[j:j + len(pat)] = rep
    n += 1
    i = j + len(pat)

print("patched occurrences:", n)
print("OLD:", OLD)
print("NEW:", NEW)

data = bytes(b)
for d in DSTS:
    try:
        open(d, "wb").write(data)
        print("written", d)
    except Exception as e:
        print("FAILED", d, e)
