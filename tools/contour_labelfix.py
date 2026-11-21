"""Bridge a bold contour across its height label: prints a manual.json fragment (a cut over the label and a
polyline joining the two bold ends). The bold ends are the two darkest, roughly opposite points on a ring of radius
R+4 around the label centre, snapped to the nearest traced line within 5 px.
usage: MAP=... CWORK=... contour_labelfix.py x,y[,R] ..."""
import os, sys, json, math, numpy as np, cv2
im = cv2.imread(os.environ['MAP']); g = cv2.GaussianBlur(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32), (0, 0), 2)
B = np.load(os.environ['CWORK'] + '/barrier.npy') if os.path.exists(os.environ['CWORK'] + '/barrier.npy') else None
S = np.load(os.environ['CWORK'] + '/skelb.npy')
out = {'cuts': [], 'raw_polylines': {}}
for spec in sys.argv[1:]:
    p = list(map(int, spec.split(','))); cx, cy = p[0], p[1]; R = p[2] if len(p) > 2 else 26
    rr = R + 4; angs = np.arange(0, 360, 2)
    vals = np.array([g[int(cy + rr * math.sin(math.radians(a))), int(cx + rr * math.cos(math.radians(a)))] for a in angs])
    i = int(np.argmin(vals)); best = None
    for j in range(len(angs)):
        d = abs((angs[j] - angs[i] + 180) % 360 - 180)
        if d >= 120 and (best is None or vals[j] < vals[best]): best = j
    ends = []
    for k in (i, best):
        x = cx + rr * math.cos(math.radians(angs[k])); y = cy + rr * math.sin(math.radians(angs[k]))
        ys, xs = np.nonzero(S[int(y) - 5:int(y) + 6, int(x) - 5:int(x) + 6])
        if len(xs):
            m = np.argmin((xs - 5) ** 2 + (ys - 5) ** 2); x, y = int(x) - 5 + xs[m], int(y) - 5 + ys[m]
        ends.append([int(x), int(y)])
    out['cuts'].append([cx, cy, R]); out['raw_polylines'][f'label_{cx}_{cy}'] = ends
    print(spec, 'ends', ends, 'darkness', int(vals[i]), int(vals[best]), file=sys.stderr)
print(json.dumps(out))
