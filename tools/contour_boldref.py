"""Second, independent count for hexes on a hill: from the dot, take the straight segment to the
nearest bold line and count the thin lines crossed on the way, then add/subtract from the bold's
known count (bold k = BOLDSTEP*k). Uses the hex's hill level (inside bold k) from the sector data.
Crossings are counted two ways: traced lines (skeleton+polylines) and dark-line peaks in the image.
usage: contour_boldref.py img skel.npy bridges.json sector.json values.json "H1,H2,.." [BOLDSTEP]"""
import sys, json, cv2, numpy as np
from scipy.signal import find_peaks
from scipy.spatial import cKDTree
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from hexgrid import center
im = cv2.imread(sys.argv[1]); g = cv2.GaussianBlur(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32), (0, 0), 1)
S = np.load(sys.argv[2]).astype(np.uint8); man = json.load(open(sys.argv[3]))
for x, y, r in man.get('cuts', []): cv2.circle(S, (int(x), int(y)), int(r), 0, -1)
for x1, y1, x2, y2 in man['bridges']: cv2.line(S, (x1, y1), (x2, y2), 1, 1)
for pl in man['polylines']: cv2.polylines(S, [np.array(pl, np.int32)], False, 1, 1)
D = cv2.dilate(S, np.ones((3, 3), np.uint8)); H, W = D.shape
sec = json.load(open(sys.argv[4]))['hexes']; val = json.load(open(sys.argv[5]))
hexes = sys.argv[6].split(','); STEP = int(sys.argv[7]) if len(sys.argv) > 7 else 4
dark = (g < 60).astype(np.uint8)
bold = cv2.morphologyEx(dark, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
n, lab, st, _ = cv2.connectedComponentsWithStats(bold, 8)
keep = np.zeros(n, bool)
for i in range(1, n): keep[i] = st[i, cv2.CC_STAT_AREA] >= 400 and max(st[i, 2], st[i, 3]) >= 120
by, bx = np.nonzero(keep[lab]); T = cKDTree(np.c_[bx, by])
def seg(p, q):
    L = int(np.hypot(q[0] - p[0], q[1] - p[1])); t = np.linspace(0, 1, max(L, 2))
    return (p[0] + (q[0] - p[0]) * t), (p[1] + (q[1] - p[1]) * t), L
for h in hexes:
    x, y = center(h); lvl = sec.get(h, {}).get('level', 0)
    d, j = T.query([x, y]); bxp, byp = bx[j], by[j]
    xs, ys, L = seg((x, y), (bxp, byp)); xi = np.clip(xs.round().astype(int), 0, W - 1); yi = np.clip(ys.round().astype(int), 0, H - 1)
    s = D[yi, xi].copy(); s[(np.arange(len(s)) < 10) | (np.arange(len(s)) > len(s) - 14)] = 0
    tr = int(((s[1:] == 1) & (s[:-1] == 0)).sum())
    prof = cv2.remap(g, xs.astype(np.float32).reshape(1, -1), ys.astype(np.float32).reshape(1, -1), cv2.INTER_LINEAR).ravel()
    bg = cv2.GaussianBlur(prof.reshape(1, -1), (31, 1), 8).ravel(); dd = bg - prof
    pk, _ = find_peaks(dd, height=25, distance=4); pk = [p for p in pk if 10 <= p <= len(prof) - 14 and prof[p] < 75]
    # which side of the bold is the dot? local level check: dot inside bold k if hex level >= k for that bold.
    # Bold count known only by ring: guess k = lvl if dot is inside (nearest bold is its own ring), else lvl+1.
    print(f"{h} level{lvl} raster {val[h]['contour']}/{val[h]['contour_max']}  nearest bold {int(d)}px at ({bxp},{byp})  thin lines between: traced {tr}, image peaks {len(pk)}")
