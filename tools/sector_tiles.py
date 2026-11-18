"""Cut a GMT hidden-setup sector image into overlaid tiles for hex-by-hex reading.
usage: sector_tiles.py <image> <outdir>"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hexgrid import center, COLS, all_hexes
from PIL import Image, ImageDraw, ImageFont
R, H = 220, 392
def verts(x, y):
    return [(x+R, y), (x+R/2, y+H/2), (x-R/2, y+H/2), (x-R, y), (x-R/2, y-H/2), (x+R/2, y-H/2)]
def main(img, out):
    os.makedirs(out, exist_ok=True)
    src = Image.open(img).convert('RGB')
    d = ImageDraw.Draw(src)
    f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 70)
    for hid in all_hexes():
        if True:
            x, y = center(hid); L, r = hid[0], int(hid[1:])
            v = verts(x, y); d.line(v + [v[0]], fill=(0, 90, 255), width=4)
            d.text((x, y + 60), f"{L}{r}", fill=(255, 0, 0), font=f, anchor='mm', stroke_width=3, stroke_fill=(255, 255, 255))
    src.save(os.path.join(out, 'overlay.jpg'), quality=85)
    n = 0
    for (c0, c1) in [(0, 4), (3, 7), (7, 10)]:
        for (y0, y1) in [(0, 2000), (1650, 3600), (3250, 5100)]:
            x0 = max(0, int(c0*330-200)); x1 = min(3300, int(c1*330+200))
            im = src.crop((x0, y0, x1, y1)); im.thumbnail((900, 1000))
            im.save(os.path.join(out, f't{n}.jpg'), quality=85); n += 1
if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
