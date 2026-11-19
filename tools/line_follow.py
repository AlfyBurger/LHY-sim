"""Hand-guided line tracing on the line-filter response: waypoints (from zoomed views) are snapped to the
strongest response within SNAP px, then consecutive waypoints are joined by the cheapest path through
the response inside a CORR px corridor around the straight segment. Output: polylines json.
usage: line_follow.py resp.npy spec.json out.json   spec: {"name": [[x,y],...], ...}"""
import sys, json, numpy as np
from skimage.graph import MCP_Geometric
SNAP, CORR = 10, 14
R = np.load(sys.argv[1]).astype(np.float32); H, W = R.shape
cost_all = 1.0 / (1.0 + np.clip(R, 0, None) / 6.0) ** 2
def snap(p):
    x, y = int(p[0]), int(p[1]); r = SNAP
    sub = R[max(y - r, 0):y + r + 1, max(x - r, 0):x + r + 1]
    j = np.unravel_index(np.argmax(sub), sub.shape)
    return (max(x - r, 0) + j[1], max(y - r, 0) + j[0])
def join(a, b):
    x0, x1 = max(min(a[0], b[0]) - CORR - 2, 0), min(max(a[0], b[0]) + CORR + 2, W - 1)
    y0, y1 = max(min(a[1], b[1]) - CORR - 2, 0), min(max(a[1], b[1]) + CORR + 2, H - 1)
    c = cost_all[y0:y1 + 1, x0:x1 + 1].copy()
    yy, xx = np.mgrid[y0:y1 + 1, x0:x1 + 1]; dx, dy = b[0] - a[0], b[1] - a[1]; L2 = dx * dx + dy * dy or 1
    t = np.clip(((xx - a[0]) * dx + (yy - a[1]) * dy) / L2, 0, 1)
    c[np.hypot(xx - (a[0] + t * dx), yy - (a[1] + t * dy)) > CORR] = np.inf
    m = MCP_Geometric(c, fully_connected=True); A = (a[1] - y0, a[0] - x0); B = (b[1] - y0, b[0] - x0)
    cum, _ = m.find_costs([A], [B])
    if not np.isfinite(cum[B]): return [a, b], 0.0
    p = m.traceback(B); pts = [(x0 + q[1], y0 + q[0]) for q in p]
    strength = float(np.mean([R[y, x] for x, y in pts]))
    return pts, strength
spec = json.load(open(sys.argv[2])); out = {}
for name, wps in spec.items():
    P = [snap(p) if not (len(p) > 2 and p[2] == '!') else (int(p[0]), int(p[1])) for p in wps]
    seq = [P[0]]; weak = []
    for i in range(len(P) - 1):
        pts, s = join(P[i], P[i + 1]); seq += pts[1:]
        if s < 20: weak.append((i, round(s)))
    out[name] = [list(map(int, q)) for q in seq[::2]] + [list(map(int, seq[-1]))]
    print(name, len(P), 'wp', ('weak segments ' + str(weak)) if weak else '')
json.dump(out, open(sys.argv[3], 'w'))
