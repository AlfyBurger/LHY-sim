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
    d.line((r - 18, r, r + 18, r), fill=(255, 0, 0), width=4); d.line((r, r - 18, r, r + 18), fill=(255, 0, 0), width=4)
    d.text((6, 4), h, fill=(255, 0, 0), font=f, stroke_width=3, stroke_fill='white')
    s.paste(t, ((i % cols) * (T + 6), (i // cols) * (T + 6)))
s.save(sys.argv[3], quality=88)
