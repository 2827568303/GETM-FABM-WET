"""Create the shared, resolution-independent lake modelling application mark.

Build-only dependency: Pillow. Geometry is shared by SVG, PNG and Windows ICO.
"""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / '3DWET/app/static/brand'


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    # Layered lake basin, computational grid, and a flowing shoreline.
    shapes = [
        ('#164657', [(69, 266), (142, 357), (269, 415), (396, 340), (447, 240), (321, 272), (195, 243)]),
        ('#257c8b', [(69, 234), (142, 325), (269, 383), (396, 308), (447, 208), (321, 240), (195, 211)]),
        ('#39b8b3', [(69, 202), (142, 293), (269, 351), (396, 276), (447, 176), (321, 208), (195, 179)]),
        ('#b0e9d7', [(69, 202), (110, 151), (178, 132), (231, 84), (300, 109), (332, 146), (412, 142), (447, 176), (396, 244), (313, 282), (269, 308), (184, 272), (142, 261)]),
        ('#148fa3', [(107, 204), (137, 175), (196, 164), (239, 120), (282, 136), (312, 175), (391, 171), (410, 181), (370, 221), (300, 252), (265, 274), (199, 248), (160, 234)]),
    ]
    lines = [((144, 198), (303, 251)), ((184, 177), (348, 231)),
             ((226, 151), (388, 202)), ((188, 242), (281, 137)),
             ((237, 262), (313, 176)), ((280, 264), (357, 175))]
    canvas = Image.new('RGBA', (2048, 2048))
    draw = ImageDraw.Draw(canvas)
    scale = 4
    draw.rounded_rectangle((0, 0, 2047, 2047), radius=440, fill='#f0f7f5')
    for color, points in shapes:
        draw.polygon([(x*scale, y*scale) for x, y in points], fill=color)
    for a, b in lines:
        draw.line([(a[0]*scale, a[1]*scale), (b[0]*scale, b[1]*scale)], fill='#79d2d5', width=10)
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><title>3DWET lake modelling</title>',
           '<rect width="512" height="512" rx="110" fill="#f0f7f5"/>']
    for color, points in shapes:
        svg.append('<polygon fill="'+color+'" points="'+' '.join(f'{x},{y}' for x,y in points)+'"/>')
    for (x1,y1),(x2,y2) in lines:
        svg.append(f'<path d="M{x1} {y1}L{x2} {y2}" fill="none" stroke="#79d2d5" stroke-width="2.5"/>')
    (DEST/'3dwet.svg').write_text(''.join(svg)+'</svg>\n', encoding='utf-8')
    for size in (32, 192, 512):
        canvas.resize((size,size), Image.Resampling.LANCZOS).save(DEST/f'3dwet-{size}.png')
    canvas.resize((256,256), Image.Resampling.LANCZOS).save(
        DEST/'3dwet.ico', sizes=[(s,s) for s in (16,24,32,48,64,128,256)])
    print(DEST)


if __name__ == '__main__':
    main()
