"""Cross-check levels against bold contour lines: find bold (thick dark) line pieces, and report the
levels on their two sides. All pieces of one bold ring should show the same pair (k-1 | k).
usage: contour_boldcheck.py canonical.jpg levels.npy out.jpg"""
import sys, cv2, numpy as np
im = cv2.imread(sys.argv[1]); g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY); L = np.load(sys.argv[2]).astype(np.int16)
dark = (g < 60).astype(np.uint8)
bold = cv2.morphologyEx(dark, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
n, lab, st, _ = cv2.connectedComponentsWithStats(bold, 8)
o = (0.5 * im + 0.5 * 255).astype(np.uint8)
res = []
for i in range(1, n):
    if st[i, cv2.CC_STAT_AREA] < 400: continue
    w, h = st[i, 2], st[i, 3]
    if max(w, h) < 120: continue
    m = (lab == i).astype(np.uint8)
    ring = cv2.dilate(m, np.ones((15, 15), np.uint8)) & (1 - cv2.dilate(m, np.ones((7, 7), np.uint8)))
    vals = L[(ring > 0) & (L >= 0)]
    if vals.size == 0: continue
    u, c = np.unique(vals, return_counts=True); top = sorted(zip(c, u), reverse=True)[:2]
    pair = tuple(sorted(int(v) for _, v in top))
    x, y = int(st[i, 0] + w / 2), int(st[i, 1] + h / 2)
    res.append((pair, x, y, int(st[i, cv2.CC_STAT_AREA])))
    o[m > 0] = (0, 0, 255)
    cv2.putText(o, f"{pair[0]}|{pair[-1]}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.6, (255, 255, 255), 9)
    cv2.putText(o, f"{pair[0]}|{pair[-1]}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.6, (150, 0, 0), 4)
for r in sorted(res, key=lambda r: (r[2], r[1])): print(r)
cv2.imwrite(sys.argv[3], cv2.resize(o, None, fx=0.3, fy=0.3, interpolation=cv2.INTER_AREA))
