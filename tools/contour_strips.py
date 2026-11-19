"""Straightened strips of the map along hex-dot to hex-dot segments, stacked into mosaics, for counting
contour lines crossing each segment. A tick marks the hexside (midpoint). The automatic count from the
line skeleton is printed next to each strip as a first guess.
usage: contour_strips.py img skel.npy pairs.txt out_prefix [per_sheet]
pairs.txt: one "H1 H2" per line."""
import sys, math, cv2, numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from hexgrid import center
im = cv2.imread(sys.argv[1]); S = np.load(sys.argv[2]).astype(np.uint8)
pairs = [l.split() for l in open(sys.argv[3]) if l.strip()]
per = int(sys.argv[5]) if len(sys.argv) > 5 else 16
HW = 30; SC = 2.0
def strip(img, p, q, interp=cv2.INTER_LINEAR):
    p = np.array(p, float); q = np.array(q, float); d = q - p; L = np.linalg.norm(d); u = d / L; n = np.array([-u[1], u[0]])
    t = np.arange(-20, L + 20, 1.0); w = np.arange(-HW, HW + 1, 1.0)
    T, Wg = np.meshgrid(t, w)
    mx = (p[0] + T * u[0] + Wg * n[0]).astype(np.float32); my = (p[1] + T * u[1] + Wg * n[1]).astype(np.float32)
    return cv2.remap(img, mx, my, interp, borderMode=cv2.BORDER_CONSTANT, borderValue=255), L
def autocount(p, q):
    s, L = strip(S * 255, p, q, cv2.INTER_NEAREST)
    core = s[HW - 6:HW + 7, 20:-20] > 0
    col = core.any(0).astype(int)
    return int(((col[1:] == 1) & (col[:-1] == 0)).sum() + col[0])
rows = []
for a, b in pairs:
    p, q = center(a), center(b)
    s, L = strip(im, p, q)
    s = cv2.resize(s, None, fx=SC, fy=SC)
    mid = int((20 + L / 2) * SC)
    cv2.line(s, (mid, 0), (mid, 10), (255, 0, 255), 3); cv2.line(s, (mid, s.shape[0] - 11), (mid, s.shape[0] - 1), (255, 0, 255), 3)
    for x in (int(20 * SC), int((20 + L) * SC)): cv2.circle(s, (x, s.shape[0] // 2), 5, (0, 0, 255), -1)
    lab = np.full((s.shape[0], 170, 3), 255, np.uint8)
    cv2.putText(lab, f"{a}>{b}", (6, 75), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 3)
    row = np.hstack([lab, s]); rows.append(row)
W = max(r.shape[1] for r in rows)
sheets = []
for k in range(0, len(rows), per):
    chunk = [np.pad(r, ((0, 6), (0, W - r.shape[1]), (0, 0)), constant_values=255) for r in rows[k:k + per]]
    out = np.vstack(chunk); fn = f"{sys.argv[4]}_{k // per}.jpg"; cv2.imwrite(fn, out, [cv2.IMWRITE_JPEG_QUALITY, 88]); sheets.append(fn)
print('\n'.join(sheets))
