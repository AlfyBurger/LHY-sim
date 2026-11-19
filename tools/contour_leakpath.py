"""Show where a contour ring leaks: shortest path through free space (not crossing any line or bridge)
between a point just inside the ring and a point just outside. usage:
contour_leakpath.py skel.npy bridges.json xin yin xout yout out.png [x0 y0 x1 y1 scale]"""
import sys, json, cv2, numpy as np
from skimage.graph import MCP_Geometric
S = np.load(sys.argv[1]).astype(np.uint8); man = json.load(open(sys.argv[2]))
for x, y, r in man.get('cuts', []): cv2.circle(S, (int(x), int(y)), int(r), 0, -1)
for x1, y1, x2, y2 in man['bridges']: cv2.line(S, (int(x1), int(y1)), (int(x2), int(y2)), 1, 1)
for pl in man.get('polylines', []): cv2.polylines(S, [np.array(pl, np.int32)], False, 1, 1)
B = cv2.dilate(S, np.ones((3, 3), np.uint8)) > 0
xi, yi, xo, yo = map(int, sys.argv[3:7])
cost = np.where(B, np.inf, 1.0)
m = MCP_Geometric(cost, fully_connected=False)
cum, _ = m.find_costs([(yi, xi)], [(yo, xo)])
if not np.isfinite(cum[yo, xo]): print('no leak: ring closed'); sys.exit(0)
path = m.traceback((yo, xo)); print('leak path length', len(path)); P = np.array([(c, r) for r, c in path])
im = cv2.imread('/home/claude/maps/reprint/10.jpg'); o = (0.6 * im + 0.4 * 255).astype(np.uint8)
o[B] = (0, 0, 200)
cv2.polylines(o, [P.astype(np.int32)], False, (255, 0, 255), 6)
cv2.circle(o, (xi, yi), 14, (0, 160, 0), -1); cv2.circle(o, (xo, yo), 14, (255, 0, 0), -1)
if len(sys.argv) > 8:
    x0, y0, x1, y1 = map(int, sys.argv[8:12]); sc = float(sys.argv[12]); o = cv2.resize(o[y0:y1, x0:x1], None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
cv2.imwrite(sys.argv[7], o)
# open ends (of the barrier skeleton) close to the leak path: where the gap is
from skimage.morphology import skeletonize as _sk
Sk = _sk(S > 0).astype(np.uint8)
nb = cv2.filter2D(Sk, -1, np.ones((3, 3), np.float32)) * Sk
ends = np.argwhere(nb == 2)
if len(ends):
    from scipy.spatial import cKDTree
    T = cKDTree(P); d, j = T.query(np.c_[ends[:, 1], ends[:, 0]])
    near = sorted({(int(ends[i, 1]), int(ends[i, 0])) for i in np.nonzero(d < 20)[0]})
    print('open ends next to the leak path:', near)
# narrowest passages: path points where free width (2 x distance to barrier) is smallest
ys_, xs_ = np.nonzero(B)
T2 = cKDTree(np.c_[xs_, ys_]); d2, _ = T2.query(P)
order = np.argsort(d2); picked = []
for i in order:
    p = tuple(int(v) for v in P[i])
    if all(abs(p[0] - q[0]) + abs(p[1] - q[1]) > 60 for q, _ in picked): picked.append((p, round(float(d2[i]), 1)))
    if len(picked) >= 6: break
print('narrowest passages (point, distance to nearest line):', picked)
