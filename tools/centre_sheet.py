"""One sheet with a close crop around every hex centre, labelled, for judging the terrain
at the centre dot (woods rule R8, colour rule R7).
usage: centre_sheet.py <image> <out.jpg> [--contrast] [--r 120]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hexgrid import center, all_hexes, COLS
from PIL import Image, ImageDraw, ImageFont, ImageOps
im = Image.open(sys.argv[1]).convert('RGB')
if "--contrast" in sys.argv: im = ImageOps.autocontrast(im, cutoff=1)
r = int(sys.argv[sys.argv.index("--r") + 1]) if "--r" in sys.argv else 120
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22)
T = 150
hexes = sorted(all_hexes(), key=lambda h: (int(h[1:]), COLS.index(h[0])))
rows = {}
for h in hexes: rows.setdefault(int(h[1:]), []).append(h)
sheet = Image.new('RGB', (len(COLS) * (T + 4), len(rows) * (T + 4)), 'black')
for ri, rr in enumerate(sorted(rows)):
    for h in rows[rr]:
        x, y = center(h); t = im.crop((int(x - r), int(y - r), int(x + r), int(y + r))).resize((T, T))
        d = ImageDraw.Draw(t); c = T // 2
        d.ellipse((c - 6, c - 6, c + 6, c + 6), outline=(255, 0, 0), width=3)
        d.text((3, 2), h, fill=(255, 0, 0), font=f, stroke_width=2, stroke_fill='white')
        sheet.paste(t, (COLS.index(h[0]) * (T + 4), ri * (T + 4)))
sheet.save(sys.argv[2], quality=88)
