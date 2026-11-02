# -*- coding: utf-8 -*-
"""Crop the toolbar row and annotate the Save (floppy) button for the user guide."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(HERE, "img", "_toolbar_src.png")
out = os.path.join(HERE, "img", "03-工具条.png")

img = Image.open(src).convert("RGB")
# toolbar icon row in toolbar_now.png (captured from screen origin 680,320)
crop = img.crop((30, 48, 1140, 122))
crop = crop.resize((crop.width * 2, crop.height * 2), Image.LANCZOS)  # 2x for readability

canvas = Image.new("RGB", (crop.width, crop.height + 58), (255, 255, 255))
canvas.paste(crop, (0, 0))
d = ImageDraw.Draw(canvas)

# floppy icon was at x≈262 in the source; after crop (-30) and 2x -> (262-30)*2 = 464
x0, y0 = 464 - 34, 14
x1, y1 = 464 + 34, 134
d.rectangle([x0, y0, x1, y1], outline=(220, 30, 30), width=4)

font = None
for path in (r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\msyhbd.ttc", r"C:\Windows\Fonts\simhei.ttf"):
    try:
        font = ImageFont.truetype(path, 30)
        break
    except Exception:
        continue
if font:
    d.text((max(0, x0 - 10), crop.height + 8), "↑ 保存（Save）", fill=(220, 30, 30), font=font)

canvas.save(out)
print("saved", out, canvas.size)
