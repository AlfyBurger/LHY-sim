"""Close gaps in a contour skeleton: (1) join any two free ends closer than NEAR px; (2) join mutually
best facing end pairs up to FAR px; (3) join remaining ends to a line straight ahead within LINE px.
Writes bridges json. usage: contour_close.py skel.npy out.json [NEAR FAR ANG LINE] [manual.json]"""
import sys, json, math, numpy as np, cv2
from skimage.morphology import skeletonize
a = sys.argv[3:]
NEAR, FAR, ANG, LINE = (float(a[0]), float(a[1]), float(a[2]), float(a[3])) if len(a) >= 4 else (30, 250, 50, 30)
man = json.load(open(a[4])) if len(a) > 4 else {'bridges': [], 'cuts': []}
S = skeletonize(np.load(sys.argv[1]) > 0).astype(np.uint8); H, W = S.shape
for x, y, r in man.get('cuts', []): cv2.circle(S, (int(x), int(y)), int(r), 0, -1)
for x1, y1, x2, y2 in man.get('bridges', []): cv2.line(S, (int(x1), int(y1)), (int(x2), int(y2)), 1, 1)
for pl in man.get('polylines', []): cv2.polylines(S, [np.array(pl, np.int32)], False, 1, 1)
S = skeletonize(S > 0).astype(np.uint8)
n, lab, st, _ = cv2.connectedComponentsWithStats(S, 8)
nb = cv2.filter2D(S, -1, np.ones((3, 3), np.float32)) * S
E = []; WALK = []
for y, x in np.argwhere(nb == 2):
    path = [(y, x)]; seen = {(y, x)}
    for _ in range(20):
        cy, cx = path[-1]; nxt = None
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                q = (cy + dy, cx + dx)
                if (dy or dx) and 0 <= q[0] < H and 0 <= q[1] < W and S[q] and q not in seen: nxt = q
        if nxt is None: break
        path.append(nxt); seen.add(nxt)
    v = np.array([x - path[-1][1], y - path[-1][0]], float); nv = np.linalg.norm(v)
    E.append((int(x), int(y), v / nv if nv else np.zeros(2), lab[y, x], len(path)))
    WALK.append({(int(c), int(r)) for r, c in path})
P = np.array([[e[0], e[1]] for e in E], float)
br = list(man.get('bridges', [])); used = set()
# (1) near ends
D = np.hypot(P[:, None, 0] - P[None, :, 0], P[:, None, 1] - P[None, :, 1]) if len(P) else np.zeros((0, 0))
pairs = sorted((D[i, j], i, j) for i in range(len(E)) for j in range(i + 1, len(E)) if D[i, j] <= NEAR)
for d, i, j in pairs:
    if i in used or j in used: continue
    if E[i][3] == E[j][3] and E[i][4] < 20: continue
    br.append([E[i][0], E[i][1], E[j][0], E[j][1]]); used |= {i, j}
# (2) facing pairs
best = {}
for i, (x, y, d, l, k) in enumerate(E):
    if i in used or k < 10: continue
    c = []
    for j in range(len(E)):
        if j == i or j in used or E[j][4] < 10: continue
        dist = D[i, j]
        if dist > FAR: continue
        u = (P[j] - P[i]) / dist
        c1, c2 = np.dot(d, u), np.dot(E[j][2], -u)
        if c1 < math.cos(math.radians(ANG)) or c2 < math.cos(math.radians(ANG)): continue
        if E[j][3] == l and dist < 30: continue
        c.append((dist * (3 - c1 - c2), j))
    if c: best[i] = min(c)[1]
for i, j in best.items():
    if best.get(j) == i and i < j:
        br.append([E[i][0], E[i][1], E[j][0], E[j][1]]); used |= {i, j}
# (3) end to line straight ahead
ys, xs = np.nonzero(S)
for i, (x, y, d, l, k) in enumerate(E):
    if i in used or k < 10: continue
    m = (np.abs(xs - x) <= LINE) & (np.abs(ys - y) <= LINE)
    sx, sy = xs[m], ys[m]; v = np.stack([sx - x, sy - y], 1).astype(float); dist = np.linalg.norm(v, axis=1)
    W_ = WALK[i]
    near_walk = np.array([any((int(px) + ddx, int(py) + ddy) in W_ for ddx in (-2, 0, 2) for ddy in (-2, 0, 2)) for px, py in zip(sx, sy)], bool) if len(sx) else np.zeros(0, bool)
    ok = (dist > 3) & (dist <= LINE) & ~near_walk
    if not ok.any(): continue
    cs = (v[ok] @ d) / dist[ok]; g = cs > math.cos(math.radians(45))
    if not g.any(): continue
    kk = np.nonzero(ok)[0][g][np.argmin(dist[ok][g])]
    br.append([x, y, int(sx[kk]), int(sy[kk])]); used.add(i)
VETO = man.get('veto', [])
nman = len(man.get('bridges', []))
br = br[:nman] + [b for b in br[nman:] if not any(min(np.hypot(b[0]-vx, b[1]-vy), np.hypot(b[2]-vx, b[3]-vy)) < 15 for vx, vy in VETO)]
json.dump({'bridges': br, 'cuts': man.get('cuts', []), 'polylines': man.get('polylines', [])}, open(sys.argv[2], 'w'))
print(len(E), 'ends;', len(br), 'bridges;', len(E) - len(used), 'ends left open')
