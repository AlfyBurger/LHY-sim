"""Map-border handling for a contour skeleton: removes the traced map border (pixels within MARGIN px of the image
edge), then extends every line end lying within REACH px of the edge straight out to the edge, so lines that run off
the map keep the bands on either side apart. Run before contour_close.py, and run contour_close.py with
CONTOUR_EDGE=3 so ends on the edge are not bridged to each other.
usage: contour_border.py skel_in.npy skel_out.npy [MARGIN REACH]"""
import sys, numpy as np, cv2
from skimage.morphology import skeletonize
S = (np.load(sys.argv[1]) > 0).astype(np.uint8); H, W = S.shape
MARGIN, REACH = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (6, 140)
S[:MARGIN] = 0; S[-MARGIN:] = 0; S[:, :MARGIN] = 0; S[:, -MARGIN:] = 0
n, lab, st, _ = cv2.connectedComponentsWithStats(S, 8)
for i in range(1, n):                                   # drop tiny leftovers of the border line
    if st[i, 4] < 40: S[lab == i] = 0
nb = cv2.filter2D(S, -1, np.ones((3, 3), np.float32)) * S
ext = 0
for y, x in np.argwhere(nb == 2):
    dists = {'L': x, 'R': W - 1 - x, 'T': y, 'B': H - 1 - y}
    side = min(dists, key=dists.get)
    if dists[side] > REACH: continue
    # direction of the line near its end (walk back ~15 px)
    path = [(y, x)]; seen = {(y, x)}
    for _ in range(15):
        cy, cx = path[-1]; nxt = None
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                q = (cy + dy, cx + dx)
                if (dy or dx) and 0 <= q[0] < H and 0 <= q[1] < W and S[q] and q not in seen: nxt = q
        if nxt is None: break
        path.append(nxt); seen.add(nxt)
    vy, vx = y - path[-1][0], x - path[-1][1]
    nv = (vx * vx + vy * vy) ** 0.5 or 1
    toward = {'L': -vx, 'R': vx, 'T': -vy, 'B': vy}[side] / nv
    if dists[side] > 40 and toward < 0.6: continue      # far ends must point at the edge
    if side in 'LR':
        tx = 0 if side == 'L' else W - 1
        ty = y if vx == 0 or (tx - x) * vx <= 0 else int(round(y + vy * (tx - x) / vx))
    else:
        ty = 0 if side == 'T' else H - 1
        tx = x if vy == 0 or (ty - y) * vy <= 0 else int(round(x + vx * (ty - y) / vy))
    if abs(tx - x) + abs(ty - y) > 3 * REACH: tx, ty = (x, ty) if side in 'TB' else (tx, y)
    cv2.line(S, (int(x), int(y)), (int(np.clip(tx, 0, W - 1)), int(np.clip(ty, 0, H - 1))), 1, 1); ext += 1
np.save(sys.argv[2], skeletonize(S > 0).astype(np.uint8))
print('ends extended to the edge:', ext)
