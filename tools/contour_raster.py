"""Contour level raster: level of a region = least number of contour lines crossed to reach open ground.
Barrier = line skeleton + bridges (auto gap links and manual bridges), dilated. For hills (no depressions)
this equals the per-hex contour counts we record (dot level, highest level inside the hexagon).
usage: contour_raster.py skel.npy chains.json manual.json out_levels.npy out.png [outside_x outside_y]
manual.json: {"bridges": [[x1,y1,x2,y2], ...], "cuts": [[x,y,r], ...]}  (cuts erase junk)"""
import sys, json, math, cv2, numpy as np
from collections import deque
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from hexgrid import all_hexes, center
S = np.load(sys.argv[1]).astype(np.uint8); H, W = S.shape
B = S.copy()
for c in (json.load(open(sys.argv[2])) if sys.argv[2] != '-' else []):
    cv2.polylines(B, [np.array(c['pts'], np.int32)], c.get('closed', False), 1, 1)
man = json.load(open(sys.argv[3])) if sys.argv[3] != '-' else {}
for x, y, r in man.get('cuts', []): cv2.circle(B, (int(x), int(y)), int(r), 0, -1)
for x1, y1, x2, y2 in man.get('bridges', []): cv2.line(B, (int(x1), int(y1)), (int(x2), int(y2)), 1, 1)
for pl in man.get('polylines', []): cv2.polylines(B, [np.array(pl, np.int32)], False, 1, 1)
from skimage.morphology import skeletonize as _skz
_sk = _skz(B > 0).astype(np.uint8)
_nb = cv2.filter2D(_sk, -1, np.ones((3, 3), np.float32)) * _sk
JUNC = cv2.dilate(((_nb >= 4) & (_sk > 0)).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))) > 0
import os
THIN = os.environ.get('CONTOUR_THIN', '1') == '1'
if THIN:
    B = _sk.copy()
else:
    B = cv2.dilate(B, np.ones((3, 3), np.uint8))
free = (B == 0).astype(np.uint8)
n, lab, st, _ = cv2.connectedComponentsWithStats(free, connectivity=4)
# region adjacency across barrier pixels (barrier 3 px wide -> look +-4 px)
ys, xs = np.nonzero(B & ~JUNC); adj = {}
OFFS = ((-2, 0), (0, -2), (-1, -1), (-1, 1), (-2, -1), (-2, 1), (-1, -2), (-1, 2)) if THIN else ((-4, 0), (0, -4), (-3, -3), (-3, 3))
for dy, dx in OFFS:
    y1, x1, y2, x2 = ys + dy, xs + dx, ys - dy, xs - dx
    ok = (y1 >= 0) & (y1 < H) & (x1 >= 0) & (x1 < W) & (y2 >= 0) & (y2 < H) & (x2 >= 0) & (x2 < W)
    a = lab[y1[ok], x1[ok]]; b = lab[y2[ok], x2[ok]]
    m = (a != b) & (a > 0) & (b > 0)
    for p, q in set(zip(a[m].tolist(), b[m].tolist())):
        adj.setdefault(p, set()).add(q); adj.setdefault(q, set()).add(p)
ox, oy = (int(sys.argv[6]), int(sys.argv[7])) if len(sys.argv) > 7 else (3250, 4950)
seeds = {lab[oy, ox]}
# every region touching the sector border with large area also counts as open ground
lev = {s: 0 for s in seeds}; q = deque(seeds)
while q:
    r = q.popleft()
    for s in adj.get(r, ()):
        if s not in lev: lev[s] = lev[r] + 1; q.append(s)
L = np.full((H, W), -1, np.int16)
lut = np.full(n, -1, np.int16)
for r, v in lev.items(): lut[r] = v
L = lut[lab]
# barrier pixels take the max of adjacent levels
Lb = L.copy(); Lb[B > 0] = -1
mx = cv2.dilate((Lb + 1).astype(np.uint8), np.ones((9, 9), np.uint8)).astype(np.int16) - 1
L[B > 0] = mx[B > 0]
np.save(sys.argv[4], L)
im = (0.5 * 255 + 0 * S).astype(np.uint8)
pal = [(245, 245, 245), (200, 235, 255), (150, 210, 255), (90, 180, 255), (40, 140, 240), (30, 90, 210), (120, 60, 200), (170, 40, 150), (210, 60, 90), (230, 120, 40), (210, 190, 30), (130, 200, 60), (60, 170, 60), (40, 120, 40)]
col = np.zeros((H, W, 3), np.uint8); col[:] = (0, 0, 0)
for v in range(0, len(pal)): col[L == v] = pal[v]
col[B > 0] = (0, 0, 0)
for h in all_hexes():
    x, y = center(h); xi, yi = int(x), int(y)
    if not (0 <= yi < H and 0 <= xi < W): continue
    pts = np.array([(int(x + 220 * math.cos(math.radians(60 * k))), int(y + 220 * math.sin(math.radians(60 * k)))) for k in range(6)])
    cv2.polylines(col, [pts], True, (255, 255, 255), 2)
    mk = np.zeros((H, W), np.uint8); cv2.fillPoly(mk, [pts], 1)
    v = L[(mk > 0) & (B == 0)]
    d = int(L[yi, xi]) if B[yi, xi] == 0 else int(max(L[max(yi - 6, 0):yi + 7, max(xi - 6, 0):xi + 7].max(), 0))
    mxv = int(v.max()) if v.size else -1
    cv2.circle(col, (xi, yi), 8, (0, 0, 0), -1)
    t = f"{h} {d}/{mxv}"
    cv2.putText(col, t, (xi - 90, yi + 50), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (255, 255, 255), 8)
    cv2.putText(col, t, (xi - 90, yi + 50), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 3)
cv2.imwrite(sys.argv[5], col)
print('regions', n, 'levelled', len(lev), 'max', max(lev.values()))
