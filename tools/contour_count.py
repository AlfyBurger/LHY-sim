"""Estimate contour elevation (number of contour lines enclosing a point) by casting
a ray from the point directly away from a hill summit and counting thin dark-line
crossings. Output is a DRAFT to check by eye.
usage: contour_count.py <image> <summit_hex> <hexes,...|auto> <out.json> <preview.jpg> [maxlen]"""
import sys, os, json, math, cv2, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hexgrid import center, all_hexes

def line_mask(img):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    bh = cv2.morphologyEx(g, cv2.MORPH_BLACKHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13)))
    S = hsv[..., 1].astype(int); V = hsv[..., 2].astype(int)
    m = (bh > 35) & (V < 110) & (S < 140)
    return m.astype(np.uint8)

def count(m, p, q, step=1.0):
    (x0, y0), (x1, y1) = p, q
    L = math.hypot(x1 - x0, y1 - y0); n = int(L / step)
    hits, last, runs = [], -100, 0
    for i in range(n):
        t = i / n; x = int(x0 + (x1 - x0) * t); y = int(y0 + (y1 - y0) * t)
        if 0 <= y < m.shape[0] and 0 <= x < m.shape[1] and m[y, x]:
            if i - last > 12: runs += 1; hits.append((x, y))
            last = i
    return runs, hits

if __name__ == "__main__":
    img = cv2.imread(sys.argv[1]); m = line_mask(img)
    sx, sy = center(sys.argv[2])
    hexes = all_hexes() if sys.argv[3] == "auto" else sys.argv[3].split(",")
    maxlen = float(sys.argv[6]) if len(sys.argv) > 6 else 1600
    res = {}; vis = img.copy()
    for h in hexes:
        x, y = center(h); dx, dy = x - sx, y - sy; d = math.hypot(dx, dy)
        if d < 1: dx, dy, d = 1.0, 0.0, 1.0
        q = (x + dx / d * maxlen, y + dy / d * maxlen)
        if h == sys.argv[2]:
            q = (x + maxlen, y)
        n, hits = count(m, (x + dx / d * 20, y + dy / d * 20), q)
        res[h] = n
        for hx, hy in hits: cv2.circle(vis, (hx, hy), 8, (255, 0, 255), 3)
        cv2.putText(vis, str(n), (int(x) - 25, int(y) + 90), cv2.FONT_HERSHEY_SIMPLEX, 2.6, (255, 255, 255), 10)
        cv2.putText(vis, str(n), (int(x) - 25, int(y) + 90), cv2.FONT_HERSHEY_SIMPLEX, 2.6, (200, 0, 0), 4)
    json.dump(res, open(sys.argv[4], "w"))
    cv2.imwrite(sys.argv[5], vis)
