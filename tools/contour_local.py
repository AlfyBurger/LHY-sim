"""Local contour count anchored on bold lines (for hills whose thin lines merge into bold ones, where
the global fewest-lines count comes out too low). Bold line k counts BOLDSTEP*k. For a point p:
band k = number of bold rings enclosing p (from the level raster: raster levels at/above the bold-k
values), b = nearest bold pixel; c = thin lines crossed on the segment p->b.
value = BOLDSTEP*kb + c if p is inside bold kb (kb == k), else BOLDSTEP*kb - 1 - c.
Dot value at the centre dot; max over a 20 px grid inside the hexagon. Also reports image-peak counts
on the dot segment as a check (woods can add false peaks; merged lines can hide traced ones).
usage: contour_local.py img skel.npy bridges.json levels.npy raster_bold_levels(e.g. 4,6) hexes|ALL_Y>=y out.json [BOLDSTEP]"""
import sys, json, math, cv2, numpy as np
from scipy.signal import find_peaks
from scipy.spatial import cKDTree
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from hexgrid import all_hexes, center
im = cv2.imread(sys.argv[1]); g = cv2.GaussianBlur(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32), (0, 0), 1)
S = np.load(sys.argv[2]).astype(np.uint8); man = json.load(open(sys.argv[3])); L = np.load(sys.argv[4])
RB = [int(v) for v in sys.argv[5].split(',')]; STEP = int(sys.argv[8]) if len(sys.argv) > 8 else 4
for x, y, r in man.get('cuts', []): cv2.circle(S, (int(x), int(y)), int(r), 0, -1)
for x1, y1, x2, y2 in man['bridges']: cv2.line(S, (x1, y1), (x2, y2), 1, 1)
for pl in man['polylines']: cv2.polylines(S, [np.array(pl, np.int32)], False, 1, 1)
H, W = S.shape
dark = (g < 60).astype(np.uint8)
bold = cv2.morphologyEx(dark, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
n, lab, st, _ = cv2.connectedComponentsWithStats(bold, 8)
keep = np.zeros(n, bool)
for i in range(1, n): keep[i] = st[i, cv2.CC_STAT_AREA] >= 400 and max(st[i, 2], st[i, 3]) >= 120
BM = keep[lab]
# bold ring number per bold component from the raster just inside it
kb_of = {}
for i in np.nonzero(keep)[0]:
    m = (lab == i).astype(np.uint8)
    ring = cv2.dilate(m, np.ones((15, 15), np.uint8)) & (1 - cv2.dilate(m, np.ones((7, 7), np.uint8)))
    v = L[(ring > 0) & (L >= 0)]
    hi = int(v.max()) if v.size else 0
    kb_of[i] = max([k + 1 for k, r in enumerate(RB) if hi >= r] or [0])
by, bx = np.nonzero(BM); T = cKDTree(np.c_[bx, by]); blab = lab[by, bx]
thin = (S > 0) & ~cv2.dilate(BM.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
D = cv2.dilate(thin.astype(np.uint8), np.ones((3, 3), np.uint8))
def band(x, y):
    v = L[y, x]
    if v < 0:
        w = L[max(y - 6, 0):y + 7, max(x - 6, 0):x + 7]; v = w.max()
    return sum(1 for r in RB if v >= r)
def value(x, y, peaks=False):
    d, j = T.query([x, y]); b = (bx[j], by[j]); kb = kb_of[blab[j]]
    if kb == 0: return None
    Ls = max(int(d), 2); t = np.linspace(0, 1, Ls)
    xs = x + (b[0] - x) * t; ys = y + (b[1] - y) * t
    s = D[np.clip(ys.round().astype(int), 0, H - 1), np.clip(xs.round().astype(int), 0, W - 1)].copy()
    c = int(((s[1:] == 1) & (s[:-1] == 0)).sum())
    k = band(x, y)
    val = STEP * kb + c if k >= kb else STEP * kb - 1 - c
    if not peaks: return val
    prof = cv2.remap(g, xs.astype(np.float32).reshape(1, -1), ys.astype(np.float32).reshape(1, -1), cv2.INTER_LINEAR).ravel()
    bg = cv2.GaussianBlur(prof.reshape(1, -1), (31, 1), 8).ravel(); dd = bg - prof
    pk, _ = find_peaks(dd, height=25, distance=4); pk = [p for p in pk if 8 <= p <= len(prof) - 12 and prof[p] < 75]
    return val, c, len(pk), kb, k, int(d)
sel = sys.argv[6]
hexes = [h for h in all_hexes() if center(h)[1] >= float(sel.split('>=')[1])] if sel.startswith('ALL_Y>=') else sel.split(',')
out = {}
for h in hexes:
    cx, cy = center(h); xi, yi = min(max(int(cx), 0), W - 1), min(max(int(cy), 0), H - 1)
    r = value(xi, yi, True)
    if r is None: continue
    dot, c, pk, kb, k, d = r
    mx = dot
    for yy in range(int(cy) - 190, int(cy) + 191, 20):
        for xx in range(int(cx) - 215, int(cx) + 216, 20):
            if abs(yy - cy) > 190 or abs(xx - cx) > 214 - abs(yy - cy) / math.sqrt(3): continue
            if not (0 <= xx < W and 0 <= yy < H) or S[yy, xx]: continue
            v = value(xx, yy)
            if v is not None and v > mx: mx = v
    out[h] = {'contour': max(dot, 0), 'contour_max': max(mx, 0), 'check': {'traced': c, 'peaks': pk, 'bold': kb, 'band': k, 'dist': d}}
json.dump(out, open(sys.argv[7], 'w'), indent=0)
for h, v in out.items(): print(h, f"{v['contour']}/{v['contour_max']}", v['check'])
