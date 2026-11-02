import struct, base64, uuid
w=h=16
row=(w*3+3)//4*4
bits=b'\x00'*(row*h)
bih=struct.pack('<IiiHHIIiiII',40,w,h,1,24,0,len(bits),2835,2835,0,0)
bmp=b'BM'+struct.pack('<IHHI',14+40+len(bits),0,0,14+40)+bih+bits
open('test16.bmp','wb').write(bmp)
print(len(bmp))
b64=base64.b64encode(bmp).decode()
open('bmp_b64.txt','w').write(b64)
js=open('hook8_template.js').read() if False else None
