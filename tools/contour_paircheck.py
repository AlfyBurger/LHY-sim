"""Compare hex dot levels with the number of traced lines crossed on the dot-to-dot segment.
|dlevel| > crossings: impossible (missing line). |dlevel| < crossings: the segment goes down and up
again (saddle, valley, rim) or a level is too low/high: check these. usage: contour_paircheck.py values.json skel.npy bridges.json"""
import sys, json, cv2, numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from hexgrid import all_hexes, center, neighbours
v = json.load(open(sys.argv[1])); S = np.load(sys.argv[2]).astype(np.uint8); man = json.load(open(sys.argv[3]))
for x, y, r in man.get('cuts', []): cv2.circle(S, (int(x), int(y)), int(r), 0, -1)
for x1, y1, x2, y2 in man['bridges']: cv2.line(S, (x1, y1), (x2, y2), 1, 1)
for pl in man['polylines']: cv2.polylines(S, [np.array(pl, np.int32)], False, 1, 1)
D = cv2.dilate(S, np.ones((3, 3), np.uint8)); H, W = D.shape
def cross(p, q):
    n = int(np.hypot(q[0] - p[0], q[1] - p[1])); t = np.linspace(0, 1, n)
    xs = np.clip((p[0] + (q[0] - p[0]) * t).round().astype(int), 0, W - 1); ys = np.clip((p[1] + (q[1] - p[1]) * t).round().astype(int), 0, H - 1)
    s = D[ys, xs].copy(); s[(t * n < 14) | (t * n > n - 14)] = 0
    return int(((s[1:] == 1) & (s[:-1] == 0)).sum())
more, less = [], []; seen = set()
for h in all_hexes():
    for n in neighbours(h):
        if not n or (n, h) in seen or n not in v: continue
        seen.add((h, n)); d = abs(v[h]['contour'] - v[n]['contour']); c = cross(center(h), center(n))
        if d > c: more.append(f"{h}-{n} d{d} c{c}")
        elif d < c: less.append(f"{h}-{n} {v[h]['contour']}>{v[n]['contour']} c{c}")
print('IMPOSSIBLE', more); print('LESS', len(less)); print(' '.join(less))
