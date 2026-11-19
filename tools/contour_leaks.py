"""Find leaking contour lines: a closed ring separates level k from k+1 along its whole length; when a
ring has an unbridged gap, both sides get the same level. Draws barrier pixels red where both sides are
equal (leaking or junk) and green where they differ, plus end points. usage: contour_leaks.py levels.npy skel.npy bridges.json bg out.png"""
import sys, json, cv2, numpy as np
L = np.load(sys.argv[1]).astype(np.int16); S = np.load(sys.argv[2]).astype(np.uint8)
for x1, y1, x2, y2 in json.load(open(sys.argv[3])).get('bridges', []): cv2.line(S, (x1, y1), (x2, y2), 1, 1)
B = cv2.dilate(S, np.ones((3, 3), np.uint8)) > 0
Lf = L.astype(np.float32); Lf[B] = np.nan
big = 10000
lo = np.where(B, big, L).astype(np.int16); hi = np.where(B, -big, L).astype(np.int16)
k = np.ones((11, 11), np.uint8)
mn = cv2.erode(lo, k); mx = cv2.dilate(hi, k)
flat = (S > 0) & (mn == mx)
step = (S > 0) & (mx > mn)
bg = cv2.imread(sys.argv[4]); o = (0.35 * bg + 0.65 * 255).astype(np.uint8)
o[cv2.dilate(step.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0] = (0, 170, 0)
o[cv2.dilate(flat.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0] = (0, 0, 255)
cv2.imwrite(sys.argv[5], o)
