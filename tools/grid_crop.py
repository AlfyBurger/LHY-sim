"""Crop of a sector image with a labelled coordinate grid (canonical pixels), for tracing lines.
usage: grid_crop.py <image> x0 y0 x1 y1 <out.jpg> [step] [scale]"""
import sys
from PIL import Image, ImageDraw, ImageFont
im = Image.open(sys.argv[1]).convert('RGB')
x0, y0, x1, y1 = map(int, sys.argv[2:6]); out = sys.argv[6]
step = int(sys.argv[7]) if len(sys.argv) > 7 else 100
sc = float(sys.argv[8]) if len(sys.argv) > 8 else 1.0
c = im.crop((x0, y0, x1, y1)); d = ImageDraw.Draw(c)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', int(22 / sc))
for x in range((x0 // step + 1) * step, x1, step):
    d.line((x - x0, 0, x - x0, y1 - y0), fill=(0, 255, 255), width=1)
    d.text((x - x0 + 3, 3), str(x), fill=(0, 0, 255), font=f, stroke_width=2, stroke_fill='white')
for y in range((y0 // step + 1) * step, y1, step):
    d.line((0, y - y0, x1 - x0, y - y0), fill=(0, 255, 255), width=1)
    d.text((3, y - y0 + 3), str(y), fill=(0, 0, 255), font=f, stroke_width=2, stroke_fill='white')
if sc != 1.0: c = c.resize((int(c.width * sc), int(c.height * sc)))
c.save(out, quality=90)
