"""Side-by-side review images: plain map (left) and Claude's overlay (right), split into halves.
usage: review_pair.py <plain.jpg> <overlay.jpg> <out_prefix> [--contrast]"""
import sys
from PIL import Image, ImageOps, ImageDraw, ImageFont
plain = Image.open(sys.argv[1]).convert('RGB'); ov = Image.open(sys.argv[2]).convert('RGB')
if "--contrast" in sys.argv: plain = ImageOps.autocontrast(plain, cutoff=1)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 60)
for name, (y0, y1) in {"north": (0, 2650), "south": (2450, 5100)}.items():
    a, b = plain.crop((0, y0, 3300, y1)), ov.crop((0, y0, 3300, y1))
    s = Image.new('RGB', (6700, y1 - y0 + 90), 'white'); d = ImageDraw.Draw(s)
    s.paste(a, (0, 90)); s.paste(b, (3400, 90))
    d.text((10, 10), "Map", fill='black', font=f); d.text((3410, 10), "Claude's reading", fill='black', font=f)
    s.thumbnail((3000, 3000)); s.save(f"{sys.argv[3]}_{name}.jpg", quality=88)
