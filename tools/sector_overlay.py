"""Draw a colour overlay of a sector's terrain data on its image, for user review.
usage: sector_overlay.py <sector.json> <image> <out.jpg>"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hexgrid import center, COLS, all_hexes, neighbours
from PIL import Image, ImageDraw, ImageFont
R, H = 220, 392
FILL = {"woods": (60, 200, 60, 90), "heavy_woods": (0, 90, 0, 120), "orchard": (180, 230, 0, 90),
        "brush": (150, 160, 60, 90), "marsh": (0, 150, 200, 90), "river": (0, 60, 255, 110)}
BLD = {"stone": (90, 90, 90), "wooden": (150, 75, 0), "urban": (60, 60, 60)}
def verts(x, y):
    return [(x+R, y), (x+R/2, y+H/2), (x-R/2, y+H/2), (x-R, y), (x-R/2, y-H/2), (x+R/2, y-H/2)]
def side(a, b):
    """Endpoints of the hexside shared by hexes a and b."""
    i = neighbours(a).index(b)
    v = verts(*center(a))
    # neighbour order N, NE, SE, S, SW, NW -> vertex pairs
    pairs = [(4, 5), (5, 0), (0, 1), (1, 2), (2, 3), (3, 4)]
    return v[pairs[i][0]], v[pairs[i][1]]
def main(js, img, out):
    d = json.load(open(js))
    im = Image.open(img).convert('RGBA'); ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); g = ImageDraw.Draw(ov)
    f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 58)
    for hid, h in d["hexes"].items():
        x, y = center(hid)
        if h.get("terrain") in FILL: g.polygon(verts(x, y), fill=FILL[h["terrain"]])
        if h.get("building"):
            g.rectangle((x-70, y-70, x+70, y+70), outline=BLD[h["building"]] + (255,), width=14)
        if h.get("hut"): g.ellipse((x+60, y-110, x+120, y-50), fill=(255, 220, 0, 230))
        if "level" in h and h["level"]: g.text((x, y-120), f"L{h['level']}", fill=(255, 0, 255, 255), font=f, anchor='mm')
    for road in d.get("roads", []):
        g.line([center(h) for h in road], fill=(255, 140, 0, 220), width=18)
    for e in d.get("roads_edges", []):
        g.line([center(e[0]), center(e[1])], fill=(255, 140, 0, 220), width=18)
    for b in d.get("buildings", []):
        g.polygon([tuple(pt) for pt in b["poly"]], outline=(255, 0, 255, 255), width=8)
    for a, b in d.get("walls", []):
        g.line(side(a, b), fill=(255, 0, 0, 255), width=22)
    for a, b in d.get("tree_lines", []):
        g.line(side(a, b), fill=(0, 255, 0, 255), width=22)
    for hid in all_hexes():
        if True:
            x, y = center(hid); L, r = hid[0], int(hid[1:]); v = verts(x, y)
            g.line(v + [v[0]], fill=(0, 90, 255, 200), width=4)
    out_im = Image.alpha_composite(im, ov).convert('RGB')
    out_im.save(out, quality=82)
if __name__ == '__main__':
    main(*sys.argv[1:4])
