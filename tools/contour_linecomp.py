"""Show the whole barrier line (skeleton+bridges+polylines connected component) passing near a point,
and its free ends: where that line stops is where a ring is open.
usage: contour_linecomp.py skel.npy bridges.json x y out.jpg [x0 y0 x1 y1 scale]"""
import sys, json, cv2, numpy as np
from skimage.morphology import skeletonize
S = np.load(sys.argv[1]).astype(np.uint8); man = json.load(open(sys.argv[2]))
for x, y, r in man.get('cuts', []): cv2.circle(S, (int(x), int(y)), int(r), 0, -1)
for x1, y1, x2, y2 in man.get('bridges', []): cv2.line(S, (int(x1), int(y1)), (int(x2), int(y2)), 1, 1)
for pl in man.get('polylines', []): cv2.polylines(S, [np.array(pl, np.int32)], False, 1, 1)
S = skeletonize(cv2.dilate(S, np.ones((3, 3), np.uint8)) > 0).astype(np.uint8)
n, lab = cv2.connectedComponents(S, connectivity=8)
x, y = int(sys.argv[3]), int(sys.argv[4])
ys, xs = np.nonzero(S[y - 12:y + 13, x - 12:x + 13]); j = np.argmin((xs - 12) ** 2 + (ys - 12) ** 2)
c = lab[y - 12 + ys[j], x - 12 + xs[j]]
C = (lab == c).astype(np.uint8)
nb = cv2.filter2D(C, -1, np.ones((3, 3), np.float32)) * C
ends = [(int(a), int(b)) for b, a in np.argwhere(nb == 2)]
print('component pixels', int(C.sum()), 'free ends', ends)
im = cv2.imread(__import__('os').environ.get('MAP', __file__.rsplit('/', 2)[0] + '/maps/reprint/10.jpg')); o = (0.6 * im + 0.4 * 255).astype(np.uint8)
o[S > 0] = (150, 150, 150); o[cv2.dilate(C, np.ones((5, 5), np.uint8)) > 0] = (0, 0, 255)
for e in ends: cv2.circle(o, e, 16, (255, 0, 255), 4)
if len(sys.argv) > 6:
    x0, y0, x1, y1 = map(int, sys.argv[6:10]); sc = float(sys.argv[10]); o = cv2.resize(o[y0:y1, x0:x1], None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
cv2.imwrite(sys.argv[5], o)
