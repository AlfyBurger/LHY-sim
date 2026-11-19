"""Generous gap bridging on a line skeleton: from every free end, connect to the nearest line pixel
ahead (within +-ANG deg of the end's heading, up to MAXD px), excluding its own stroke. Extra bridges
are harmless for the least-crossings level raster (they only split bands); missing ones make levels leak.
usage: contour_bridges.py skel.npy chains.json out_bridges.json [maxd] [ang]"""
import sys, json, math, cv2, numpy as np
from collections import deque
S = np.load(sys.argv[1]).astype(np.uint8)
for c in json.load(open(sys.argv[2])):
    cv2.polylines(S, [np.array(c['pts'], np.int32)], c.get('closed', False), 1, 1)
S = (S > 0).astype(np.uint8)
from skimage.morphology import skeletonize
S = skeletonize(S > 0).astype(np.uint8)
MAXD = float(sys.argv[4]) if len(sys.argv) > 4 else 260; ANG = float(sys.argv[5]) if len(sys.argv) > 5 else 40
H, W = S.shape
nb = cv2.filter2D(S, -1, np.ones((3, 3), np.float32)) * S
ends = list(zip(*np.nonzero(nb == 2)))
n, lab = cv2.connectedComponents(S, connectivity=8)
ys_all, xs_all = np.nonzero(S)
def walk_back(y, x, k=18):
    path = [(y, x)]; seen = {(y, x)}
    for _ in range(k):
        cy, cx = path[-1]; nxt = None
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                q = (cy + dy, cx + dx)
                if (dy or dx) and 0 <= q[0] < H and 0 <= q[1] < W and S[q] and q not in seen: nxt = q
        if nxt is None: break
        path.append(nxt); seen.add(nxt)
    return path
bridges = []
endset = {(int(x), int(y)) for (y, x) in ends}
END_ONLY_BEYOND = float(sys.argv[6]) if len(sys.argv) > 6 else 1e9
cand = {}
for (y, x) in ends:
    p = walk_back(y, x)
    if len(p) < 8: continue
    d = np.array([x - p[-1][1], y - p[-1][0]], float); d /= (np.linalg.norm(d) + 1e-9)
    R = int(MAXD)
    y0, y1, x0, x1 = max(y - R, 0), min(y + R + 1, H), max(x - R, 0), min(x + R + 1, W)
    sy, sx = np.nonzero(S[y0:y1, x0:x1]); sy = sy + y0; sx = sx + x0
    v = np.stack([sx - x, sy - y], 1).astype(float); dist = np.linalg.norm(v, axis=1)
    ok = (dist > 4) & (dist <= MAXD)
    own = lab[sy, sx] == lab[y, x]
    # own stroke allowed only if far along it (closing a ring): require dist > 60 and not in last walked pixels
    walked = set(p)
    ok &= ~own | (dist > 60)
    if not ok.any(): continue
    cosang = (v[ok] @ d) / dist[ok]
    good = cosang > math.cos(math.radians(ANG))
    if not good.any(): continue
    idx = np.nonzero(ok)[0][good]; cg = cosang[good]
    score = dist[idx] * (1 + 2.0 * (1 - cg))
    # beyond END_ONLY_BEYOND px, only accept targets that are free ends facing back
    order = np.argsort(score)
    for jj in order[:400]:
        j = idx[jj]
        if dist[j] > END_ONLY_BEYOND:
            near_end = any((int(sx[j]) + ddx, int(sy[j]) + ddy) in endset for ddx in range(-6, 7) for ddy in range(-6, 7))
            if not near_end: continue
        bridges.append([int(x), int(y), int(sx[j]), int(sy[j])]); break
json.dump({'bridges': bridges}, open(sys.argv[3], 'w'))
print(len(ends), 'ends', len(bridges), 'bridges')
