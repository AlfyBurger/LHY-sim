"""Full-resolution crops around hex centre dots (dot marked with a small cross), for
counting the contour lines between a dot and the open ground or summit by eye.
usage: contour_sheet.py <image> <hexes,...> <out.jpg> [radius]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hexgrid import center
from PIL import Image, ImageDraw, ImageFont
im = Image.open(sys.argv[1]).convert('RGB'); hexes = sys.argv[2].split(",")
r = int(sys.argv[4]) if len(sys.argv) > 4 else 260
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 34)
T = 2 * r; cols = 5; rows = (len(hexes) + cols - 1) // cols
s = Image.new('RGB', (cols * (T + 6), rows * (T + 6)), 'black')
for i, h in enumerate(hexes):
    x, y = center(h); t = im.crop((int(x - r), int(y - r), int(x + r), int(y + r)))
    d = ImageDraw.Draw(t)
    R, HH = 220, 392
    v = [(r + R, r), (r + R / 2, r + HH / 2), (r - R / 2, r + HH / 2), (r - R, r), (r - R / 2, r - HH / 2), (r + R / 2, r - HH / 2)]
    d.line(v + [v[0]], fill=(255, 0, 0), width=3)
    d.ellipse((r - 9, r - 9, r + 9, r + 9), outline=(255, 0, 0), width=3)
    d.text((6, 4), h, fill=(255, 0, 0), font=f, stroke_width=3, stroke_fill='white')
    s.paste(t, ((i % cols) * (T + 6), (i // cols) * (T + 6)))
s.save(sys.argv[3], quality=88)
