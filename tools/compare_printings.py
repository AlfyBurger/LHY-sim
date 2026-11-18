"""Side-by-side of a sector in both printings on the same hex grid.
usage: compare_printings.py <sector> <out.jpg> [rows a-b]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hexgrid import center, COLS, all_hexes
from PIL import Image, ImageDraw, ImageFont, ImageOps
R, H = 220, 392
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 64)
def grid(im):
    d = ImageDraw.Draw(im)
    for hid in all_hexes():
        if True:
            x, y = center(hid); L, r = hid[0], int(hid[1:])
            v = [(x+R, y), (x+R/2, y+H/2), (x-R/2, y+H/2), (x-R, y), (x-R/2, y-H/2), (x+R/2, y-H/2)]
            d.line(v + [v[0]], fill=(0, 90, 255), width=5)
            d.text((x, y+70), f"{L}{r}", fill=(255, 0, 0), font=f, anchor='mm', stroke_width=3, stroke_fill='white')
    return im
n = sys.argv[1]; out = sys.argv[2]
r0, r1 = (int(t) for t in (sys.argv[3].split('-') if len(sys.argv) > 3 else ('1', '13')))
y0, y1 = max(0, int(195 + (r0-1)*392 - 250)), min(5100, int(391 + (r1-1)*392 + 250))
a = Image.open(f"/home/claude/maps/original/{n}.jpg").convert('RGB')
a = ImageOps.autocontrast(a, cutoff=1)   # undo the wash for comparison
b = Image.open(f"/home/claude/maps/reprint/{n}.jpg").convert('RGB')
a, b = grid(a).crop((0, y0, 3300, y1)), grid(b).crop((0, y0, 3300, y1))
w, h = a.size
s = Image.new('RGB', (2*w + 60, h), 'white'); s.paste(a, (0, 0)); s.paste(b, (w + 60, 0))
s.thumbnail((2000, 2000)); s.save(out, quality=85)
