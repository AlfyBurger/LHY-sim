"""Line skeleton of a sector image for contour work.
1. Oriented line filter response (dark thin lines), hysteresis threshold, skeleton.
2. Hex-grid marks: skeleton pixels within 7 px of a hex edge, within 95 px of a vertex, running along that
   edge (+-22 deg) are removed (vertex "tripods"); pieces lying wholly inside a vertex zone, a hex-label
   box or a centre dot are removed. Contour lines that cross those zones are kept.
3. Spurs shorter than T px and isolated pieces shorter than M px are pruned.
usage: contour_skeleton.py resp.npy out.npy [lo hi T M]"""
import sys, math, numpy as np, cv2
from skimage.filters import apply_hysteresis_threshold
from skimage.morphology import skeletonize
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from hexgrid import all_hexes, center
from skan import Skeleton, summarize
R = np.load(sys.argv[1]); a = sys.argv[3:]
lo, hi = (float(a[0]), float(a[1])) if len(a) >= 2 else (28, 50)
T, M = (float(a[2]), float(a[3])) if len(a) >= 4 else (35, 70)
from skimage.morphology import remove_small_holes
S = skeletonize(remove_small_holes(apply_hysteresis_threshold(R, lo, hi), 60)).astype(np.uint8); H, W = S.shape
# local direction of skeleton pixels from structure tensor of the skeleton
Sf = S.astype(np.float32)
gx = cv2.Sobel(cv2.GaussianBlur(Sf, (0, 0), 3), cv2.CV_32F, 1, 0); gy = cv2.Sobel(cv2.GaussianBlur(Sf, (0, 0), 3), cv2.CV_32F, 0, 1)
Jxx = cv2.GaussianBlur(gx * gx, (0, 0), 4); Jyy = cv2.GaussianBlur(gy * gy, (0, 0), 4); Jxy = cv2.GaussianBlur(gx * gy, (0, 0), 4)
theta = 0.5 * np.arctan2(2 * Jxy, Jxx - Jyy)          # gradient direction; line direction = theta + 90
ldir = (np.degrees(theta) + 90) % 180
edge_zone = np.zeros((H, W), np.uint8); edge_ang = np.zeros((H, W), np.float32)
vert_zone = np.zeros((H, W), np.uint8); text_zone = np.zeros((H, W), np.uint8)
verts = set()
for h in all_hexes():
    x, y = center(h)
    P = [(x + 220 * math.cos(math.radians(60 * k)), y + 220 * math.sin(math.radians(60 * k))) for k in range(6)]
    for k in range(6):
        p, q = P[k], P[(k + 1) % 6]; ang = math.degrees(math.atan2(q[1] - p[1], q[0] - p[0])) % 180
        for v, w in ((p, q), (q, p)):
            d = np.array(w) - np.array(v); d /= np.linalg.norm(d); e = np.array(v) + d * 95
            tmp = np.zeros((H, W), np.uint8); cv2.line(tmp, (int(v[0]), int(v[1])), (int(e[0]), int(e[1])), 1, 15)
            edge_zone |= tmp; edge_ang[tmp > 0] = ang
        verts.add((int(round(p[0])), int(round(p[1]))))
    cv2.rectangle(text_zone, (int(x) - 55, int(y) - 165), (int(x) + 55, int(y) - 85), 1, -1)
    cv2.circle(text_zone, (int(x), int(y)), 20, 1, -1)
for vx, vy in verts: cv2.circle(vert_zone, (vx, vy), 95, 1, -1)
dd = np.abs((ldir - edge_ang + 90) % 180 - 90)
S[(edge_zone > 0) & (dd < 22) & (S > 0)] = 0
cv2.circle  # noqa
for vx, vy in verts: cv2.circle(S, (vx, vy), 6, 0, -1)
# remove pieces wholly inside vertex or text zones
n, lab, st, _ = cv2.connectedComponentsWithStats(S, 8)
inside = np.ones(n, bool)
zone = (vert_zone | text_zone) > 0
outs = np.bincount(lab[(S > 0) & ~zone], minlength=n)
inside = outs == 0; inside[0] = False
S[inside[lab]] = 0
# prune
S = skeletonize(S > 0)
for it in range(5):
    sk = Skeleton(S); df = summarize(sk, separator='_')
    kill = df[((df['branch_type'] == 1) & (df['branch_distance'] < T)) | ((df['branch_type'] == 0) & (df['branch_distance'] < M))]
    if len(kill) == 0: break
    for i in kill.index:
        for (r, c) in sk.path_coordinates(i).astype(int): S[r, c] = False
    for i in df.drop(kill.index).index:
        for (r, c) in sk.path_coordinates(i).astype(int): S[r, c] = True
    S = skeletonize(S)
np.save(sys.argv[2], S)
nb = cv2.filter2D(S.astype(np.uint8), -1, np.ones((3, 3), np.float32)) * S
print('pixels', int(S.sum()), 'ends', int((nb == 2).sum()))
