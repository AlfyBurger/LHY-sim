"""Track several nearly-parallel contour lines column by column (good where lines run close together
and the skeleton merges them). Start positions on one column; step west or east; at each column take
the nearest darkness peak to the extrapolated position. Reports columns where two lines take the same
peak (true merge or ambiguity). usage: column_track.py img x_start x_end step y1,y2,... out.json [axis]
axis 'x' (default): lines run roughly east-west, positions are y on columns.
axis 'y': lines run roughly north-south, positions are x on rows."""
import sys, json, cv2, numpy as np
from scipy.signal import find_peaks
im = cv2.imread(sys.argv[1]); g = cv2.GaussianBlur(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32), (0, 0), 1.0)
a, b, st = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]); ys = [float(v) for v in sys.argv[5].split(',')]
axis = sys.argv[7] if len(sys.argv) > 7 else 'x'
if axis == 'y': g = g.T
def peaks(x, lo, hi):
    col = g[int(lo):int(hi), x - 2:x + 3].mean(1); bg = cv2.GaussianBlur(col.reshape(-1, 1), (1, 31), 8).ravel(); d = bg - col
    pk, pr = find_peaks(d, height=12, distance=3)
    return [lo + p for p in pk], d[pk]
tracks = [[(a, y)] for y in ys]; vel = [0.0] * len(ys); clashes = []
for x in range(a + (st if b > a else -st), b + (st if b > a else -st), st if b > a else -st):
    pred = [t[-1][1] + v for t, v in zip(tracks, vel)]
    pk, h = peaks(x, min(pred) - 30, max(pred) + 30)
    used = {}
    for i, p in enumerate(pred):
        if len(pk) == 0: tracks[i].append((x, p)); continue
        j = int(np.argmin([abs(q - p) for q in pk]))
        y = pk[j] if abs(pk[j] - p) <= 9 else p
        if abs(pk[j] - p) <= 9: used.setdefault(j, []).append(i)
        vel[i] = 0.6 * vel[i] + 0.4 * (y - tracks[i][-1][1]); tracks[i].append((x, float(y)))
    for j, ii in used.items():
        if len(ii) > 1: clashes.append((x, [int(i) for i in ii]))
out = [[(int(x), int(round(y))) if axis == 'x' else (int(round(y)), int(x)) for x, y in t] for t in tracks]
json.dump(out, open(sys.argv[6], 'w'))
print('clashes (column, lines sharing a peak):', clashes[:30], '...' if len(clashes) > 30 else '')
for i, t in enumerate(out): print(i, t[:: max(1, len(t) // 8)])
