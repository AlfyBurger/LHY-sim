"""Scan transects: between each two consecutive line crossings is a band; two neighbouring bands
that are the same free-space region mean the line between them is open somewhere (a leak).
usage: contour_leakscan.py skel.npy bridges.json "y=1700:1500-3300" "x=980:100-2700" ..."""
import sys, json, cv2, numpy as np
S = np.load(sys.argv[1]).astype(np.uint8); man = json.load(open(sys.argv[2]))
for x, y, r in man.get('cuts', []): cv2.circle(S, (int(x), int(y)), int(r), 0, -1)
for x1, y1, x2, y2 in man.get('bridges', []): cv2.line(S, (int(x1), int(y1)), (int(x2), int(y2)), 1, 1)
for pl in man.get('polylines', []): cv2.polylines(S, [np.array(pl, np.int32)], False, 1, 1)
B = cv2.dilate(S, np.ones((3, 3), np.uint8)) > 0
n, lab = cv2.connectedComponents((~B).astype(np.uint8), connectivity=4)
total = 0
for spec in sys.argv[3:]:
    ax, rest = spec.split('='); c, rng = rest.split(':'); a, b = map(int, rng.split('-')); c = int(c)
    v = lab[c, a:b] if ax == 'y' else lab[a:b, c]
    bands = []; i = 0
    while i < len(v):
        if v[i] == 0: i += 1; continue
        j = i
        while j < len(v) and v[j] == v[i]: j += 1
        if j - i >= 4: bands.append((v[i], a + i, a + j))
        i = j
    leaks = [(bands[k][2], bands[k + 1][1]) for k in range(len(bands) - 1) if bands[k][0] == bands[k + 1][0]]
    total += len(leaks)
    print(spec, 'bands', len(bands), 'leaky lines at', [f"{ax}={c},{'x' if ax == 'y' else 'y'}~{(p + q) // 2}" for p, q in leaks])
print('total leaks', total)
