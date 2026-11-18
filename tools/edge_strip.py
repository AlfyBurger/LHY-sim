"""Tiles of every edge half hex of a sector, labelled, for checking edge terrain.
usage: edge_strip.py <image> <out.jpg> [--contrast]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hexgrid import center, all_hexes
from PIL import Image, ImageDraw, ImageFont, ImageOps
im = Image.open(sys.argv[1]).convert('RGB')
if "--contrast" in sys.argv: im = ImageOps.autocontrast(im, cutoff=1)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 40)
edge = [h for h in all_hexes() if h[0] in "AK" or h[1:] == "0" or (h[1:] == "13" and h[0] in "BDFHJ")]
tiles = []
for h in edge:
    x, y = center(h); t = im.crop((int(x - 230), int(y - 210), int(x + 230), int(y + 210)))
    d = ImageDraw.Draw(t); d.text((10, 5), h, fill=(255, 0, 0), font=f, stroke_width=3, stroke_fill='white')
    d.ellipse((220, 200, 240, 220), outline=(255, 0, 0), width=4)
    tiles.append(t.resize((230, 210)))
cols = 9; rows = (len(tiles) + cols - 1) // cols
s = Image.new('RGB', (cols * 232, rows * 212), 'black')
for i, t in enumerate(tiles): s.paste(t, ((i % cols) * 232, (i // cols) * 212))
s.save(sys.argv[2], quality=85); print(len(edge), "edge hexes")
