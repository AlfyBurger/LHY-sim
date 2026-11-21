"""Colour the free-space region (between lines) containing a point, to see where a band leaks.
usage: contour_region.py skel.npy bridges.json x y out.jpg [x0 y0 x1 y1 scale]"""
import sys, json, cv2, numpy as np
S = np.load(sys.argv[1]).astype(np.uint8); man = json.load(open(sys.argv[2]))
for x, y, r in man.get('cuts', []): cv2.circle(S, (int(x), int(y)), int(r), 0, -1)
for x1, y1, x2, y2 in man.get('bridges', []): cv2.line(S, (int(x1), int(y1)), (int(x2), int(y2)), 1, 1)
for pl in man.get('polylines', []): cv2.polylines(S, [np.array(pl, np.int32)], False, 1, 1)
B = cv2.dilate(S, np.ones((3, 3), np.uint8)) > 0
n, lab = cv2.connectedComponents((~B).astype(np.uint8), connectivity=4)
x, y = int(sys.argv[3]), int(sys.argv[4]); r = lab[y, x]
im = cv2.imread(__import__('os').environ.get('MAP', __file__.rsplit('/', 2)[0] + '/maps/reprint/10.jpg')); o = (0.55 * im + 0.45 * 255).astype(np.uint8)
o[lab == r] = (0.5 * o[lab == r] + 0.5 * np.array([255, 0, 255])).astype(np.uint8)
o[B] = (0, 0, 200)
if len(sys.argv) > 6:
    x0, y0, x1, y1 = map(int, sys.argv[6:10]); sc = float(sys.argv[10]); o = cv2.resize(o[y0:y1, x0:x1], None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
cv2.imwrite(sys.argv[5], o)
