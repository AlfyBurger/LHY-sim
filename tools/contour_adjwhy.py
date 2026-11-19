"""Why does a band get its level? List neighbouring regions (across one line) with their levels and
sample points where they touch. usage: contour_adjwhy.py levels.npy skel.npy bridges.json x y"""
import sys, json, cv2, numpy as np
from skimage.morphology import skeletonize
L = np.load(sys.argv[1]); S = np.load(sys.argv[2]).astype(np.uint8); man = json.load(open(sys.argv[3]))
for x, y, r in man.get('cuts', []): cv2.circle(S, (int(x), int(y)), int(r), 0, -1)
for x1, y1, x2, y2 in man.get('bridges', []): cv2.line(S, (int(x1), int(y1)), (int(x2), int(y2)), 1, 1)
for pl in man.get('polylines', []): cv2.polylines(S, [np.array(pl, np.int32)], False, 1, 1)
sk = skeletonize(S > 0).astype(np.uint8); nb = cv2.filter2D(sk, -1, np.ones((3, 3), np.float32)) * sk
J = cv2.dilate(((nb >= 4) & (sk > 0)).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))) > 0
B = cv2.dilate(S, np.ones((3, 3), np.uint8)) > 0
n, lab = cv2.connectedComponents((~B).astype(np.uint8), connectivity=4)
x, y = int(sys.argv[4]), int(sys.argv[5]); r = lab[y, x]; H, W = B.shape
ys, xs = np.nonzero(B & ~J); res = {}
for dy, dx in ((-4, 0), (0, -4), (-3, -3), (-3, 3)):
    y1, x1, y2, x2 = ys + dy, xs + dx, ys - dy, xs - dx
    ok = (y1 >= 0) & (y1 < H) & (x1 >= 0) & (x1 < W) & (y2 >= 0) & (y2 < H) & (x2 >= 0) & (x2 < W)
    a = lab[y1[ok], x1[ok]]; b = lab[y2[ok], x2[ok]]; px, py = xs[ok], ys[ok]
    for A_, B_, X, Y in ((a, b, px, py), (b, a, px, py)):
        m = (A_ == r) & (B_ != r) & (B_ > 0)
        for o, xx, yy in zip(B_[m], X[m], Y[m]):
            res.setdefault(int(o), []).append((int(xx), int(yy)))
print('region level', L[y, x])
for o, pts in sorted(res.items(), key=lambda t: L[lab == t[0]][0] if (lab == t[0]).any() else 99):
    lv = int(L[lab == o][0]); pts = sorted(set(pts))
    print(' neighbour level', lv, 'touch points', len(pts), 'e.g.', pts[:: max(1, len(pts) // 6)][:6])
