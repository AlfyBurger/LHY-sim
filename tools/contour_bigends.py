"""Free ends of the large line components (likely gaps) inside a box.
usage: contour_bigends.py skel.npy bridges.json x0 y0 x1 y1 [minpix]"""
import sys, json, cv2, numpy as np
from skimage.morphology import skeletonize
S = np.load(sys.argv[1]).astype(np.uint8); man = json.load(open(sys.argv[2]))
for x, y, r in man.get('cuts', []): cv2.circle(S, (int(x), int(y)), int(r), 0, -1)
for x1, y1, x2, y2 in man.get('bridges', []): cv2.line(S, (int(x1), int(y1)), (int(x2), int(y2)), 1, 1)
for pl in man.get('polylines', []): cv2.polylines(S, [np.array(pl, np.int32)], False, 1, 1)
S = skeletonize(cv2.dilate(S, np.ones((3, 3), np.uint8)) > 0).astype(np.uint8)
x0, y0, x1, y1 = map(int, sys.argv[3:7]); mp = int(sys.argv[7]) if len(sys.argv) > 7 else 1500
n, lab, st, _ = cv2.connectedComponentsWithStats(S, 8)
nb = cv2.filter2D(S, -1, np.ones((3, 3), np.float32)) * S
out = []
for y, x in np.argwhere(nb == 2):
    if not (x0 <= x < x1 and y0 <= y < y1): continue
    if st[lab[y, x], cv2.CC_STAT_AREA] < mp: continue
    if x < 8 or y < 8 or x > S.shape[1] - 9 or y > S.shape[0] - 9: continue
    out.append((int(x), int(y)))
print(len(out)); print(' '.join(f'"{i}:{x},{y}"' for i, (x, y) in enumerate(out)))
