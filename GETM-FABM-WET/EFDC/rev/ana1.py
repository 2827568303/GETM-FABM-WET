import struct, binascii
d=open('dump_1.bin','rb').read()
print('len',len(d))
print('head',binascii.hexlify(d[:64]).decode())
print('ascii', d[:64])
# try parse as bmp file
if d[:2]==b'BM':
    print('BMP file header', struct.unpack('<2sIHHI', d[:14]))
else:
    print('not BM')
# try parse as BITMAPINFOHEADER at 0
print('biSize', struct.unpack('<I', d[:4])[0])
for off in range(0, 16):
    sz=struct.unpack('<I', d[off:off+4])[0]
    if sz in (12,40,108,124):
        print('possible BITMAPINFOHEADER at offset', off, 'biSize', sz,
              struct.unpack('<iiHHIIiiII', d[off:off+40]) if off+40<=len(d) else '')
# try pillow
from PIL import Image
import io
try:
    im=Image.open(io.BytesIO(d)); print('PIL opened', im.format, im.size, im.mode)
except Exception as e:
    print('PIL failed:', e)
# try as ico
try:
    im=Image.open(io.BytesIO(d)); im.load(); print('loaded ok')
except Exception as e:
    print('load failed', e)
