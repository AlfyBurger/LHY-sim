"""Cross-check contour numbers: for each pair of adjacent hexes, count dark thin-line
crossings on the segment between their centre dots and compare with the difference of
their recorded contours. Woods texture can add false crossings, so pairs where either
hex is wooded are reported separately.
usage: contour_check.py <sector.json> <image> [--all]"""
import sys, os, json, cv2, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hexgrid import center, all_hexes, neighbours

def mask(img):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    bh = cv2.morphologyEx(g, cv2.MORPH_BLACKHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))
    return (bh > 80) & (g < 80)

def crossings(m, p, q):
    (x0, y0), (x1, y1) = p, q
    n = int(np.hypot(x1 - x0, y1 - y0)); runs = 0; last = -99
    for i in range(18, n - 18):  # skip the dots
        t = i / n; x, y = int(round(x0 + (x1 - x0) * t)), int(round(y0 + (y1 - y0) * t))
        hit = m[y-1:y+2, x-1:x+2].any()
        if hit:
            if i - last > 6: runs += 1
            last = i
    return runs

if __name__ == "__main__":
    d = json.load(open(sys.argv[1])); img = cv2.imread(sys.argv[2]); m = mask(img)
    H = d["hexes"]; c = lambda h: H.get(h, {}).get("contour", 0)
    wooded = lambda h: H.get(h, {}).get("terrain") in ("woods", "heavy_woods")
    bad, woody = [], []
    for a in all_hexes():
        for b in neighbours(a):
            if not b or b < a: continue
            if c(a) == 0 and c(b) == 0 and "--all" not in sys.argv: 
                k = crossings(m, center(a), center(b))
                if k == 0: continue
            k = crossings(m, center(a), center(b)); diff = abs(c(a) - c(b))
            if k != diff:
                (woody if wooded(a) or wooded(b) else bad).append((a, b, c(a), c(b), k))
    print("MISMATCH (open ground):"); [print("  %s-%s  contours %d/%d  lines crossed %d" % t) for t in bad]
    print("mismatch involving woods (texture may add crossings):"); [print("  %s-%s  contours %d/%d  lines crossed %d" % t) for t in woody]
