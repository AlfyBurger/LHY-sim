"""List barrier line pieces whose two sides have the same level ("flat"): junk strokes, or real lines
that are open (leak) or mis-joined. Long flat pieces need a look.
usage: contour_flat.py levels.npy skel.npy bridges.json [minlen]"""
import sys, json, cv2, numpy as np
L = np.load(sys.argv[1]).astype(np.int16); S = np.load(sys.argv[2]).astype(np.uint8); man = json.load(open(sys.argv[3]))
for x, y, r in man.get('cuts', []): cv2.circle(S, (int(x), int(y)), int(r), 0, -1)
for x1, y1, x2, y2 in man.get('bridges', []): cv2.line(S, (int(x1), int(y1)), (int(x2), int(y2)), 1, 1)
for pl in man.get('polylines', []): cv2.polylines(S, [np.array(pl, np.int32)], False, 1, 1)
B = cv2.dilate(S, np.ones((3, 3), np.uint8)) > 0
lo = np.where(B, 10000, L).astype(np.int16); hi = np.where(B, -10000, L).astype(np.int16)
k = np.ones((11, 11), np.uint8); flat = ((S > 0) & (cv2.erode(lo, k) == cv2.dilate(hi, k))).astype(np.uint8)
ml = int(sys.argv[4]) if len(sys.argv) > 4 else 120
n, lab, st, _ = cv2.connectedComponentsWithStats(cv2.dilate(flat, np.ones((3, 3), np.uint8)), 8)
out = []
for i in range(1, n):
    if st[i, cv2.CC_STAT_AREA] / 3 < ml: continue
    ys, xs = np.nonzero(lab == i); j = len(xs) // 2
    o = np.argsort(xs + ys)[j]
    out.append((int(st[i, cv2.CC_STAT_AREA] / 3), int(xs[o]), int(ys[o])))
out.sort(reverse=True)
print(len(out), 'flat pieces'); print(' '.join(f'"{k}:{x},{y}"' for k, (l, x, y) in enumerate(out)))
print([l for l, _, _ in out])
