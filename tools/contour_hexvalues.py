"""Per-hex contour values from a level raster: 'contour' = level at the centre dot (band containing the
dot; if the dot sits on a line, the higher side), 'contour_max' = highest band level inside the hexagon
(clipped to the sector). usage: contour_hexvalues.py levels.npy skel.npy bridges.json out.json"""
import sys, json, math, cv2, numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from hexgrid import all_hexes, center
L = np.load(sys.argv[1]).astype(np.int16); S = np.load(sys.argv[2]).astype(np.uint8); man = json.load(open(sys.argv[3]))
for x, y, r in man.get('cuts', []): cv2.circle(S, (int(x), int(y)), int(r), 0, -1)
for x1, y1, x2, y2 in man.get('bridges', []): cv2.line(S, (int(x1), int(y1)), (int(x2), int(y2)), 1, 1)
for pl in man.get('polylines', []): cv2.polylines(S, [np.array(pl, np.int32)], False, 1, 1)
B = cv2.dilate(S, np.ones((3, 3), np.uint8)) > 0; H, W = L.shape
out = {}
for h in all_hexes():
    x, y = center(h)
    pts = np.array([(int(x + 218 * math.cos(math.radians(60 * k))), int(y + 218 * math.sin(math.radians(60 * k)))) for k in range(6)])
    m = np.zeros((H, W), np.uint8); cv2.fillPoly(m, [pts], 1)
    v = L[(m > 0) & ~B & (L >= 0)]
    xi, yi = min(max(int(x), 0), W - 1), min(max(int(y), 0), H - 1)
    win = L[max(yi - 8, 0):yi + 9, max(xi - 8, 0):xi + 9]; wb = B[max(yi - 8, 0):yi + 9, max(xi - 8, 0):xi + 9]
    vals = win[~wb & (win >= 0)]
    dot = int(vals.max()) if vals.size else 0
    out[h] = {'contour': dot, 'contour_max': int(v.max()) if v.size else dot}
json.dump(out, open(sys.argv[4], 'w'), indent=0)
print(len(out), 'hexes')
