"""Sheet of every road hex of a sector with its current terrain label, to check the
terrain under the road (4.1.9b: TEM comes from the other terrain in a road hex).
usage: road_audit.py <sector.json> <image> <out.jpg>"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hexgrid import center
from PIL import Image, ImageDraw, ImageFont
d = json.load(open(sys.argv[1])); im = Image.open(sys.argv[2]).convert('RGB')
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 26)
hexes = []
for r in d.get("roads", []):
    for h in r:
        if not h.startswith("@") and h not in hexes: hexes.append(h)
T = 220; cols = 8; rows = (len(hexes) + cols - 1) // cols
s = Image.new('RGB', (cols * (T + 4), rows * (T + 4)), 'black')
for i, h in enumerate(hexes):
    x, y = center(h); t = im.crop((int(x - 230), int(y - 210), int(x + 230), int(y + 210))).resize((T, T))
    lab = d["hexes"].get(h, {}).get("terrain", "open")
    g = ImageDraw.Draw(t); g.text((4, 2), h, fill=(255, 0, 0), font=f, stroke_width=3, stroke_fill='white')
    g.text((4, T - 30), lab, fill=(0, 0, 255) if lab != "open" else (0, 0, 0), font=f, stroke_width=3, stroke_fill='white')
    s.paste(t, ((i % cols) * (T + 4), (i // cols) * (T + 4)))
s.save(sys.argv[3], quality=85); print(len(hexes), "road hexes")
