"""Contour review image: plain map (left) and the reading (right): traced lines and, at every hex dot,
'dot/max' (contour count at the centre dot / highest count inside the hexagon). Hexes listed in --flag
get a magenta ring. usage: contour_review.py img skel.npy bridges.json values.json y0 y1 out.jpg [--flag H1,H2]"""
import sys, json, math, cv2, numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from hexgrid import all_hexes, center
im = cv2.imread(sys.argv[1]); S = np.load(sys.argv[2]).astype(np.uint8); man = json.load(open(sys.argv[3]))
v = json.load(open(sys.argv[4])); y0, y1 = int(sys.argv[5]), int(sys.argv[6])
flags = sys.argv[sys.argv.index('--flag') + 1].split(',') if '--flag' in sys.argv else []
for x, y, r in man.get('cuts', []): cv2.circle(S, (int(x), int(y)), int(r), 0, -1)
for x1, y1_, x2, y2 in man.get('bridges', []): cv2.line(S, (x1, y1_), (x2, y2), 1, 1)
for pl in man.get('polylines', []): cv2.polylines(S, [np.array(pl, np.int32)], False, 1, 1)
o = (0.55 * im + 0.45 * 255).astype(np.uint8)
o[cv2.dilate(S, np.ones((3, 3), np.uint8)) > 0] = (40, 40, 220)
for h in all_hexes():
    x, y = center(h)
    pts = np.array([(int(x + 220 * math.cos(math.radians(60 * k))), int(y + 220 * math.sin(math.radians(60 * k)))) for k in range(6)])
    cv2.polylines(o, [pts], True, (200, 170, 120), 2)
    if h in flags: cv2.circle(o, (int(x), int(y)), 120, (200, 0, 200), 8)
    d = v[h]; t = f"{d['contour']}/{d['contour_max']}"
    if d['contour'] == '-': continue
    cv2.circle(o, (int(x), int(y)), 9, (0, 0, 0), -1)
    cv2.putText(o, h, (int(x) - 40, int(y) - 40), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (90, 90, 90), 3)
    cv2.putText(o, t, (int(x) - 60, int(y) + 70), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (255, 255, 255), 12)
    cv2.putText(o, t, (int(x) - 60, int(y) + 70), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 0, 0), 5)
a = im[y0:y1]; b = o[y0:y1]
s = np.full((y1 - y0 + 100, 6700, 3), 255, np.uint8); s[100:, :3300] = a; s[100:, 3400:] = b
cv2.putText(s, "Map", (10, 75), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 0, 0), 5)
cv2.putText(s, "Claude's reading: contour lines at the dot / highest inside the hex", (3410, 75), cv2.FONT_HERSHEY_SIMPLEX, 2.2, (0, 0, 0), 5)
sc = 3000 / 6700
cv2.imwrite(sys.argv[7], cv2.resize(s, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 88])
