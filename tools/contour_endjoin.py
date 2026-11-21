"""Join each loose line end to the traced line it continues into (typically across a hex-corner mark, where the
corner cleanup erased a stretch of the contour). From the end, the cheapest path through the line-filter response
is searched inside a cone ahead of the end (half-angle CONE deg, radius RAD px) until it meets any traced line other
than the end's own stretch; the join is kept if the mean and 10th-percentile response along it are high enough.
Prints candidates; writes accepted joins as raw_polylines (names ej_x_y).
usage: CWORK=... contour_endjoin.py out.json [RAD CONE MINMEAN MINP10] [x,y ...  (only these ends)]"""
import os, sys, json, math, numpy as np, cv2
from skimage.morphology import skeletonize
from skimage.graph import MCP_Geometric
W = os.environ['CWORK']; a = [v for v in sys.argv[2:] if ',' not in v]; only = [tuple(map(int, v.split(','))) for v in sys.argv[2:] if ',' in v]
RAD, CONE, MINMEAN, MINP10 = (float(v) for v in a) if len(a) == 4 else (170, 55, 18, 5)
R = np.load(f'{W}/resp.npy').astype(np.float32); B = skeletonize(np.load(f'{W}/barrier.npy') > 0).astype(np.uint8)
H, Wd = B.shape; EDGE = 4
nb = cv2.filter2D(B, -1, np.ones((3, 3), np.float32)) * B
cost = 1.0 / (1.0 + np.clip(R, 0, None) / 6.0) ** 2
out = {}
for y, x in np.argwhere(nb == 2):
    if not (EDGE <= x < Wd - EDGE and EDGE <= y < H - EDGE): continue
    if only and min(math.hypot(x - p[0], y - p[1]) for p in only) > 12: continue
    path = [(y, x)]; seen = {(y, x)}
    for _ in range(60):
        cy, cx = path[-1]; nxt = None
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                q = (cy + dy, cx + dx)
                if (dy or dx) and 0 <= q[0] < H and 0 <= q[1] < Wd and B[q] and q not in seen: nxt = q
        if nxt is None: break
        path.append(nxt); seen.add(nxt)
    if len(path) < 12: continue
    v = np.array([x - path[min(20, len(path) - 1)][1], y - path[min(20, len(path) - 1)][0]], float); v /= (np.linalg.norm(v) or 1)
    r = int(RAD); x0, y0, x1, y1 = max(x - r, 0), max(y - r, 0), min(x + r, Wd - 1), min(y + r, H - 1)
    yy, xx = np.mgrid[y0:y1 + 1, x0:x1 + 1]; dx, dy = xx - x, yy - y; dist = np.hypot(dx, dy)
    cosang = (dx * v[0] + dy * v[1]) / np.maximum(dist, 1e-6)
    cone = (dist <= RAD) & ((cosang >= math.cos(math.radians(CONE))) | (dist < 4))
    own = np.zeros_like(B[y0:y1 + 1, x0:x1 + 1], bool)
    for (py, px) in path: 
        if y0 <= py <= y1 and x0 <= px <= x1: own[py - y0, px - x0] = True
    own = cv2.dilate(own.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
    bar = (B[y0:y1 + 1, x0:x1 + 1] > 0) & ~own
    c = cost[y0:y1 + 1, x0:x1 + 1].copy(); c[~cone] = np.inf
    m = MCP_Geometric(c, fully_connected=True); cum, _ = m.find_costs([(y - y0, x - x0)])
    tg = np.argwhere(bar & np.isfinite(cum))
    if not len(tg): continue
    best = None
    for ty, tx in tg[np.argsort(cum[tg[:, 0], tg[:, 1]])[:40]]:
        pts = [(x0 + q[1], y0 + q[0]) for q in m.traceback((ty, tx))]
        # path must not cross other lines before the target
        if any(bar[py - y0, px - x0] for px, py in pts[:-1]): continue
        rr = np.array([R[py, px] for px, py in pts]); s = (float(rr.mean()), float(np.percentile(rr, 10)), len(pts), pts)
        if best is None or s[0] + s[1] > best[0] + best[1]: best = s
    if best is None: continue
    mean, p10, n, pts = best; ok = mean >= MINMEAN and p10 >= MINP10 and n >= 6
    print(f"{'ACCEPT' if ok else 'reject'} end ({x},{y}) -> ({pts[-1][0]},{pts[-1][1]}) len={n} mean={mean:.0f} p10={p10:.0f}")
    if ok: out[f'ej_{x}_{y}'] = [list(map(int, q)) for q in pts[::3]] + [list(map(int, pts[-1]))]
json.dump(out, open(sys.argv[1], 'w')); print(len(out), 'joins written')
