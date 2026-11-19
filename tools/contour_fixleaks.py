"""Iteratively close gaps in leaking contour rings.
Each round: level raster -> line pixels with equal levels on both sides ("flat") -> free ends of long
flat strokes -> bridge mutually-best facing pairs whose straight bridge crosses no other line -> repeat.
usage: contour_fixleaks.py skel.npy bridges_in.json bridges_out.json rounds [maxd]"""
import sys, json, math, subprocess, cv2, numpy as np
from skimage.morphology import skeletonize
from collections import deque
T = __file__.rsplit('/', 1)[0]
skel, bin_, bout, rounds = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
MAXD = float(sys.argv[5]) if len(sys.argv) > 5 else 450
br = json.load(open(bin_))['bridges']
S0 = np.load(skel).astype(np.uint8)
for it in range(rounds):
    json.dump({'bridges': br}, open('/tmp/_br.json', 'w'))
    subprocess.run(['python3', f'{T}/contour_raster.py', skel, '-', '/tmp/_br.json', '/tmp/_L.npy', '/tmp/_L.png'], check=True, capture_output=True)
    L = np.load('/tmp/_L.npy').astype(np.int16)
    S = S0.copy()
    for x1, y1, x2, y2 in br: cv2.line(S, (x1, y1), (x2, y2), 1, 1)
    S = skeletonize(S > 0).astype(np.uint8)
    B = cv2.dilate(S, np.ones((3, 3), np.uint8)) > 0
    lo = np.where(B, 10000, L).astype(np.int16); hi = np.where(B, -10000, L).astype(np.int16)
    k = np.ones((11, 11), np.uint8); flat = (S > 0) & (cv2.erode(lo, k) == cv2.dilate(hi, k))
    F = flat.astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(F, 8)
    nb = cv2.filter2D(S, -1, np.ones((3, 3), np.float32)) * S   # ends of the full skeleton
    E = []
    for y, x in np.argwhere((nb == 2) & flat):
        if st[lab[y, x], cv2.CC_STAT_AREA] < 150: continue
        path = [(y, x)]; seen = {(y, x)}
        for _ in range(20):
            cy, cx = path[-1]; nxt = None
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    q = (cy + dy, cx + dx)
                    if (dy or dx) and 0 <= q[0] < S.shape[0] and 0 <= q[1] < S.shape[1] and S[q] and q not in seen: nxt = q
            if nxt is None: break
            path.append(nxt); seen.add(nxt)
        if len(path) < 10: continue
        d = np.array([x - path[-1][1], y - path[-1][0]], float); d /= np.linalg.norm(d) + 1e-9
        E.append((int(x), int(y), d, lab[y, x]))
    P = np.array([[e[0], e[1]] for e in E], float) if E else np.zeros((0, 2))
    def clear(a, b):
        n = int(np.hypot(b[0] - a[0], b[1] - a[1]))
        for t in range(8, n - 8):
            x = int(round(a[0] + (b[0] - a[0]) * t / n)); y = int(round(a[1] + (b[1] - a[1]) * t / n))
            if B[y, x]: return False
        return True
    best = {}
    for i, (x, y, d, l) in enumerate(E):
        v = P - P[i]; dist = np.linalg.norm(v, axis=1); c = []
        for j in np.nonzero((dist > 2) & (dist <= MAXD))[0]:
            u = v[j] / dist[j]; c1 = np.dot(d, u); c2 = np.dot(E[j][2], -u)
            if c1 < math.cos(math.radians(60)) or c2 < math.cos(math.radians(60)): continue
            if L[y, x] != L[E[j][1], E[j][0]] and False: continue
            c.append((dist[j] * (3 - c1 - c2), j))
        c.sort()
        for s, j in c[:5]:
            if clear((x, y), (E[j][0], E[j][1])): best[i] = j; break
    new = []
    for i, j in best.items():
        if best.get(j) == i and i < j: new.append([E[i][0], E[i][1], E[j][0], E[j][1]])
    print('round', it, 'flat ends', len(E), 'new bridges', len(new))
    if not new: break
    br += new
json.dump({'bridges': br}, open(bout, 'w'))
