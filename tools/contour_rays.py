"""Rays from a centre with every skeleton crossing numbered, to pick ring waypoints by (ray, index).
usage: contour_rays.py skel.npy bg.png cx cy nrays rmax out.png out.json [x0 y0 x1 y1 scale]"""
import sys, json, math, cv2, numpy as np
S = np.load(sys.argv[1]).astype(bool); bg = cv2.imread(sys.argv[2])
cx, cy, nr, rmax = float(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5]), float(sys.argv[6])
out = {}
for k in range(nr):
    th = 2 * math.pi * k / nr; xs = []; last = -99
    for t in np.arange(15, rmax, 1.0):
        x, y = int(round(cx + t * math.cos(th))), int(round(cy + t * math.sin(th)))
        if not (0 <= x < S.shape[1] and 0 <= y < S.shape[0]): break
        hit = S[max(y - 1, 0):y + 2, max(x - 1, 0):x + 2].any()
        if hit and t - last > 7: xs.append((x, y)); last = t
        elif hit: last = t
    out[k] = xs
    ex, ey = int(cx + rmax * math.cos(th)), int(cy + rmax * math.sin(th))
    cv2.line(bg, (int(cx), int(cy)), (ex, ey), (0, 160, 255), 2)
    cv2.putText(bg, f"r{k}", (ex, ey), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 120, 255), 4)
    for i, (x, y) in enumerate(xs):
        cv2.circle(bg, (x, y), 6, (0, 0, 255), -1)
        cv2.putText(bg, str(i), (x + 6, y - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 5)
        cv2.putText(bg, str(i), (x + 6, y - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (200, 0, 0), 2)
json.dump(out, open(sys.argv[8], 'w'))
if len(sys.argv) > 9:
    x0, y0, x1, y1 = map(int, sys.argv[9:13]); sc = float(sys.argv[13])
    bg = cv2.resize(bg[y0:y1, x0:x1], None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
cv2.imwrite(sys.argv[7], bg)
