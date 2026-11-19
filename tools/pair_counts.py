"""Count line crossings on every dot-to-dot segment from a line skeleton; draw the count at each
hexside midpoint over a background (for visual verification).
usage: pair_counts.py skel.npy bg.png out.json out.png"""
import sys, json, math, cv2, numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from hexgrid import all_hexes, center, neighbours
S = np.load(sys.argv[1]).astype(np.uint8)
D = cv2.dilate(S, np.ones((3, 3), np.uint8))
def count(p, q):
    p = np.array(p, float); q = np.array(q, float); L = np.linalg.norm(q - p); n = int(L)
    ts = np.linspace(0, 1, n); xs = (p[0] + (q[0] - p[0]) * ts).round().astype(int); ys = (p[1] + (q[1] - p[1]) * ts).round().astype(int)
    ok = (xs >= 0) & (xs < S.shape[1]) & (ys >= 0) & (ys < S.shape[0])
    v = np.zeros(n, int); v[ok] = D[ys[ok], xs[ok]]
    # ignore the dot neighbourhoods
    v[(ts * L < 20) | (ts * L > L - 20)] = 0
    runs = []; i = 0
    while i < n:
        if v[i]:
            j = i
            while j < n and v[j]: j += 1
            runs.append(round(float((i + j) / 2 / n), 3)); i = j
        else: i += 1
    return runs
res = {}; seen = set()
for h in all_hexes():
    for nb in neighbours(h):
        if nb is None or (nb, h) in seen: continue
        seen.add((h, nb)); res[f"{h}-{nb}"] = count(center(h), center(nb))
json.dump(res, open(sys.argv[3], 'w'))
bg = cv2.imread(sys.argv[2])
for k, r in res.items():
    a, b = k.split('-'); p, q = center(a), center(b)
    m = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
    if not r: continue
    t = str(len(r)); col = (0, 0, 200)
    cv2.putText(bg, t, (int(m[0]) - 12, int(m[1]) + 14), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 9)
    cv2.putText(bg, t, (int(m[0]) - 12, int(m[1]) + 14), cv2.FONT_HERSHEY_SIMPLEX, 1.4, col, 4)
cv2.imwrite(sys.argv[4], bg)
print(sum(1 for r in res.values() if r), 'pairs with crossings of', len(res))
