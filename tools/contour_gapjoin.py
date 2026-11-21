"""Join gaps between loose line ends along the drawn line (lines hidden under woods, faded stretches).
For each pair of loose ends within DMAX px that roughly face each other, finds the cheapest path through the
line-filter response inside a CORR px corridor, never touching another traced line, and scores it by the mean
and 10th-percentile response along the path. Pairs are accepted greedily, best first, each end used once.
Prints the candidates; writes accepted joins as raw_polylines (names gap_x_y) to a json fragment.
usage: CWORK=... contour_gapjoin.py out.json [DMAX CORR MINMEAN MINP10 ANG]"""
import os, sys, json, math, numpy as np, cv2
from skimage.morphology import skeletonize
from skimage.graph import MCP_Geometric
W = os.environ['CWORK']; a = sys.argv[2:]
DMAX, CORR, MINMEAN, MINP10, ANG = (float(v) for v in a) if len(a) == 5 else (320, 45, 18, 5, 80)
CORR = int(CORR)
R = np.load(f'{W}/resp.npy').astype(np.float32); B = skeletonize(np.load(f'{W}/barrier.npy') > 0).astype(np.uint8)
H, Wd = B.shape; EDGE = 4
nb = cv2.filter2D(B, -1, np.ones((3, 3), np.float32)) * B
ends = []
for y, x in np.argwhere(nb == 2):
    if not (EDGE <= x < Wd - EDGE and EDGE <= y < H - EDGE): continue
    path = [(y, x)]; seen = {(y, x)}
    for _ in range(20):
        cy, cx = path[-1]; nxt = None
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                q = (cy + dy, cx + dx)
                if (dy or dx) and 0 <= q[0] < H and 0 <= q[1] < Wd and B[q] and q not in seen: nxt = q
        if nxt is None: break
        path.append(nxt); seen.add(nxt)
    if len(path) < 12: continue                         # tiny specks/spurs: no direction
    v = np.array([x - path[-1][1], y - path[-1][0]], float); v /= (np.linalg.norm(v) or 1)
    ends.append((int(x), int(y), v, {(int(c), int(r)) for r, c in path}))
cost = 1.0 / (1.0 + np.clip(R, 0, None) / 6.0) ** 2
cand = []
for i in range(len(ends)):
    for j in range(i + 1, len(ends)):
        (x1, y1, v1, w1), (x2, y2, v2, w2) = ends[i], ends[j]
        d = math.hypot(x2 - x1, y2 - y1)
        if d < 6 or d > DMAX: continue
        u = np.array([x2 - x1, y2 - y1]) / d
        if np.dot(v1, u) < math.cos(math.radians(ANG)) or np.dot(v2, -u) < math.cos(math.radians(ANG)): continue
        x0, x1b = max(min(x1, x2) - CORR - 2, 0), min(max(x1, x2) + CORR + 2, Wd - 1)
        y0, y1b = max(min(y1, y2) - CORR - 2, 0), min(max(y1, y2) + CORR + 2, H - 1)
        c = cost[y0:y1b + 1, x0:x1b + 1].copy()
        yy, xx = np.mgrid[y0:y1b + 1, x0:x1b + 1]; dx, dy = x2 - x1, y2 - y1
        t = np.clip(((xx - x1) * dx + (yy - y1) * dy) / (d * d), 0, 1)
        c[np.hypot(xx - (x1 + t * dx), yy - (y1 + t * dy)) > CORR] = np.inf
        bl = cv2.dilate(B[y0:y1b + 1, x0:x1b + 1], np.ones((5, 5), np.uint8)) > 0
        keep = (np.hypot(xx - x1, yy - y1) < 6) | (np.hypot(xx - x2, yy - y2) < 6)
        c[bl & ~keep] = np.inf
        m = MCP_Geometric(c, fully_connected=True); A = (y1 - y0, x1 - x0); Bp = (y2 - y0, x2 - x0)
        cum, _ = m.find_costs([A], [Bp])
        if not np.isfinite(cum[Bp]): continue
        pts = [(x0 + q[1], y0 + q[0]) for q in m.traceback(Bp)]
        r = np.array([R[py, px] for px, py in pts])
        mean, p10 = float(r.mean()), float(np.percentile(r, 10))
        cand.append((mean, p10, d, i, j, pts))
cand.sort(key=lambda t: -(t[0] + t[1]))
used = set(); out = {}
for mean, p10, d, i, j, pts in cand:
    ok = mean >= MINMEAN and p10 >= MINP10 and i not in used and j not in used
    print(f"{'ACCEPT' if ok else 'reject'} ({ends[i][0]},{ends[i][1]})-({ends[j][0]},{ends[j][1]}) d={d:.0f} mean={mean:.0f} p10={p10:.0f}")
    if ok:
        used |= {i, j}; out[f'gap_{ends[i][0]}_{ends[i][1]}'] = [list(map(int, q)) for q in pts[::3]] + [list(map(int, pts[-1]))]
json.dump(out, open(sys.argv[1], 'w')); print(len(out), 'joins written')
