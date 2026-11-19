"""Print band levels along a transect from the level raster (after contour_raster.py).
usage: contour_transect.py levels.npy skel.npy bridges.json "y=1350:100-1700" ..."""
import sys, json, cv2, numpy as np
L = np.load(sys.argv[1]); S = np.load(sys.argv[2]).astype(np.uint8); man = json.load(open(sys.argv[3]))
for x, y, r in man.get('cuts', []): cv2.circle(S, (int(x), int(y)), int(r), 0, -1)
for x1, y1, x2, y2 in man.get('bridges', []): cv2.line(S, (int(x1), int(y1)), (int(x2), int(y2)), 1, 1)
for pl in man.get('polylines', []): cv2.polylines(S, [np.array(pl, np.int32)], False, 1, 1)
B = cv2.dilate(S, np.ones((3, 3), np.uint8)) > 0
for spec in sys.argv[4:]:
    ax, rest = spec.split('='); c, rng = rest.split(':'); a, b = map(int, rng.split('-')); c = int(c)
    lv = L[c, a:b] if ax == 'y' else L[a:b, c]; bb = B[c, a:b] if ax == 'y' else B[a:b, c]
    out = []; i = 0
    while i < len(lv):
        if bb[i]: i += 1; continue
        j = i
        while j < len(lv) and not bb[j] and lv[j] == lv[i]: j += 1
        if j - i >= 4: out.append(f"{a + i}-{a + j}:{lv[i]}")
        i = j
    print(spec, ' '.join(out))
