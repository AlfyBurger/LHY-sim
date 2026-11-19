"""Trace contour lines from hand-picked waypoints, snapped onto the line skeleton.

Each waypoint snaps to the nearest skeleton pixel within SNAP px (prefix the point with "!" in the
spec, i.e. [x, y, "!"], to keep it as given, e.g. where a line is hidden under a road). Consecutive
waypoints are joined by the cheapest path along the skeleton inside a corridor of CORR px around the
straight segment (so a path cannot jump to the neighbouring line); if no skeleton path exists the
segment is drawn straight and reported as a gap.

usage: ring_trace.py skel.npy spec.json out.json
spec.json: {"name": {"closed": true|false, "pts": [[x,y], [x,y,"!"], ...]}, ...}"""
import sys, json, math
import numpy as np, cv2
from skimage.graph import MCP_Geometric

SNAP, CORR = 22, 16

def snap(S, p):
    x, y = int(p[0]), int(p[1]); r = SNAP
    sub = S[max(y - r, 0):y + r + 1, max(x - r, 0):x + r + 1]
    ys, xs = np.nonzero(sub)
    if len(xs) == 0: return (x, y), False
    xs = xs + max(x - r, 0); ys = ys + max(y - r, 0)
    j = np.argmin((xs - x) ** 2 + (ys - y) ** 2)
    if (xs[j] - x) ** 2 + (ys[j] - y) ** 2 > r * r: return (x, y), False
    return (int(xs[j]), int(ys[j])), True

def join(S, a, b):
    x0, x1 = min(a[0], b[0]) - CORR - 2, max(a[0], b[0]) + CORR + 2
    y0, y1 = min(a[1], b[1]) - CORR - 2, max(a[1], b[1]) + CORR + 2
    x0, y0 = max(x0, 0), max(y0, 0)
    sub = S[y0:y1 + 1, x0:x1 + 1]
    cost = np.where(sub > 0, 1.0, 40.0)
    # corridor mask
    yy, xx = np.mgrid[y0:y0 + sub.shape[0], x0:x0 + sub.shape[1]]
    ax, ay, bx, by = a[0], a[1], b[0], b[1]
    dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy or 1
    t = np.clip(((xx - ax) * dx + (yy - ay) * dy) / L2, 0, 1)
    dist = np.hypot(xx - (ax + t * dx), yy - (ay + t * dy))
    cost[dist > CORR] = np.inf
    A = (a[1] - y0, a[0] - x0); B = (b[1] - y0, b[0] - x0)
    m = MCP_Geometric(cost, fully_connected=True)
    cum, _ = m.find_costs([A], [B])
    if not np.isfinite(cum[B]): return [a, b], 1.0
    path = m.traceback(B)
    pts = [(int(x0 + c), int(y0 + r)) for r, c in path]
    off = sum(1 for (x, y) in pts if not S[y, x]) / max(len(pts), 1)
    return pts, off

if __name__ == '__main__':
    S = np.load(sys.argv[1]).astype(np.uint8)
    S = cv2.dilate(S, np.ones((3, 3), np.uint8))
    spec = json.load(open(sys.argv[2])); out = {}
    for name, r in spec.items():
        W = []
        for p in r['pts']:
            if len(p) > 2 and p[2] == '!': W.append(((int(p[0]), int(p[1])), True, True))
            else:
                q, ok = snap(S, p); W.append((q, ok, False))
        miss = [i for i, w in enumerate(W) if not w[1]]
        seq = [W[0][0]]; gaps = []
        n = len(W) if r.get('closed') else len(W) - 1
        for i in range(n):
            a, b = W[i][0], W[(i + 1) % len(W)][0]
            if W[i][2] or W[(i + 1) % len(W)][2]:
                pts, off = [a, b], 1.0
            else:
                pts, off = join(S, a, b)
            if off > 0.35: gaps.append(i)
            seq.extend(pts[1:])
        out[name] = {'closed': r.get('closed', False), 'pts': [list(p) for p in seq[::2]] + ([list(seq[-1])] if len(seq) % 2 == 0 else [])}
        flag = (' unsnapped wp ' + str(miss) if miss else '') + (' gaps after wp ' + str(gaps) if gaps else '')
        print(f"{name}: {len(W)} wp{flag}")
    json.dump(out, open(sys.argv[3], 'w'))
