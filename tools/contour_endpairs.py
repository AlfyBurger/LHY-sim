"""Bridges between facing free ends (mutual best), plus short end-to-line bridges.
usage: contour_endpairs.py skel.npy out.json [maxd_end] [ang] [maxd_line]"""
import sys, json, math, cv2, numpy as np
from skimage.morphology import skeletonize
S = skeletonize(np.load(sys.argv[1]) > 0).astype(np.uint8); H, W = S.shape
MAXE = float(sys.argv[3]) if len(sys.argv) > 3 else 160; ANG = float(sys.argv[4]) if len(sys.argv) > 4 else 45
MAXL = float(sys.argv[5]) if len(sys.argv) > 5 else 30
n, lab, st, _ = cv2.connectedComponentsWithStats(S, 8)
nb = cv2.filter2D(S, -1, np.ones((3, 3), np.float32)) * S
E = []
for y, x in np.argwhere(nb == 2):
    if st[lab[y, x], cv2.CC_STAT_AREA] < 40: continue
    path = [(y, x)]; seen = {(y, x)}
    for _ in range(20):
        cy, cx = path[-1]; nxt = None
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                q = (cy + dy, cx + dx)
                if (dy or dx) and 0 <= q[0] < H and 0 <= q[1] < W and S[q] and q not in seen: nxt = q
        if nxt is None: break
        path.append(nxt); seen.add(nxt)
    if len(path) < 10: continue
    d = np.array([x - path[-1][1], y - path[-1][0]], float); d /= np.linalg.norm(d) + 1e-9
    E.append((int(x), int(y), d, lab[y, x]))
P = np.array([[e[0], e[1]] for e in E], float)
best = {}
for i, (x, y, d, l) in enumerate(E):
    v = P - P[i]; dist = np.linalg.norm(v, axis=1)
    c = []
    for j in np.nonzero((dist > 2) & (dist <= MAXE))[0]:
        u = v[j] / dist[j]
        if np.dot(d, u) < math.cos(math.radians(ANG)): continue
        if np.dot(E[j][2], -u) < math.cos(math.radians(ANG)): continue
        if E[j][3] == l and dist[j] < 80: continue
        c.append((dist[j] * (3 - np.dot(d, u) - np.dot(E[j][2], -u)), j))
    if c: best[i] = min(c)[1]
br = []; used = set()
for i, j in best.items():
    if best.get(j) == i and i < j:
        br.append([E[i][0], E[i][1], E[j][0], E[j][1]]); used |= {i, j}
# short end-to-line bridges for unused ends
ys, xs = np.nonzero(S)
for i, (x, y, d, l) in enumerate(E):
    if i in used: continue
    m = (np.abs(xs - x) <= MAXL) & (np.abs(ys - y) <= MAXL)
    sx, sy = xs[m], ys[m]; v = np.stack([sx - x, sy - y], 1).astype(float); dist = np.linalg.norm(v, axis=1)
    ok = (dist > 3) & (dist <= MAXL) & (lab[sy, sx] != l)
    if not ok.any(): continue
    cs = (v[ok] @ d) / dist[ok]; g = cs > math.cos(math.radians(60))
    if not g.any(): continue
    k = np.nonzero(ok)[0][g][np.argmin(dist[ok][g])]
    br.append([x, y, int(sx[k]), int(sy[k])])
json.dump({'bridges': br}, open(sys.argv[2], 'w'))
print(len(E), 'ends', len(br), 'bridges')
