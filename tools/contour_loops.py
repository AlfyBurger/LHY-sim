"""Closed contour lines as minimum-cost loops around a centre, through seed points.

Cost is low on dark thin lines (oriented line-filter response) and high elsewhere. For a seed on a line
and a centre inside the ring, the plane is cut along the ray centre->seed->outwards and the cheapest
path from one side of the seed to the other is computed: it must go around the centre, and following
the line all the way round is far cheaper than crossing open ground, so the loop is the line itself.
Seeds can be given, or found automatically where rays from the centre cross the line skeleton.

usage: contour_loops.py resp.npy skel.npy centre_x centre_y out.json [--rays N] [--seeds x,y;x,y..] [--win R]
Each loop gets 'q' = share of its length running on line pixels (response >= QTH); low q = suspect.
"""
import sys, json, math, argparse
import numpy as np
from skimage.graph import MCP_Geometric

QTH = 25.0

def loop_through(R, cost, c, seed, win):
    H, W = R.shape
    x0, y0 = max(int(c[0] - win), 0), max(int(c[1] - win), 0)
    x1, y1 = min(int(c[0] + win), W - 1), min(int(c[1] + win), H - 1)
    sub = cost[y0:y1 + 1, x0:x1 + 1].copy()
    cx, cy = c[0] - x0, c[1] - y0; sx, sy = seed[0] - x0, seed[1] - y0
    d = np.array([sx - cx, sy - cy], float); L = np.linalg.norm(d); d /= L; n = np.array([-d[1], d[0]])
    # block the ray from centre outwards (3 px wide)
    for t in np.arange(0, 2 * win * 1.5, 0.5):
        for w in (-1, 0, 1):
            x, y = int(round(cx + d[0] * t + n[0] * w * 0.7)), int(round(cy + d[1] * t + n[1] * w * 0.7))
            if 0 <= x < sub.shape[1] and 0 <= y < sub.shape[0]: sub[y, x] = np.inf
    A = (int(round(sy + n[1] * 3)), int(round(sx + n[0] * 3)))
    B = (int(round(sy - n[1] * 3)), int(round(sx - n[0] * 3)))
    if not (np.isfinite(sub[A]) and np.isfinite(sub[B])): return None
    m = MCP_Geometric(sub, fully_connected=True)
    cum, _ = m.find_costs([A], [B])
    if not np.isfinite(cum[B]): return None
    path = m.traceback(B)
    pts = [(int(x0 + p[1]), int(y0 + p[0])) for p in path]
    return pts, float(cum[B])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('resp'); ap.add_argument('skel'); ap.add_argument('cx', type=float); ap.add_argument('cy', type=float)
    ap.add_argument('out'); ap.add_argument('--rays', type=int, default=0); ap.add_argument('--seeds', default='')
    ap.add_argument('--win', type=int, default=1500); ap.add_argument('--rmax', type=float, default=1400)
    ap.add_argument("--prefix", default="L"); ap.add_argument("--soft", type=float, default=7.0)
    a = ap.parse_args()
    R = np.load(a.resp).astype(np.float32); S = np.load(a.skel).astype(bool)
    cost = (np.exp(-np.clip(R, 0, None) / a.soft) + 0.001).astype(np.float64)
    c = (a.cx, a.cy); seeds = []
    if a.seeds:
        seeds = [tuple(map(float, s.split(','))) for s in a.seeds.split(';')]
    for k in range(a.rays):
        th = 2 * math.pi * k / a.rays
        last = -99
        for t in np.arange(20, a.rmax, 1.0):
            x, y = int(round(c[0] + t * math.cos(th))), int(round(c[1] + t * math.sin(th)))
            if not (0 <= x < S.shape[1] and 0 <= y < S.shape[0]): break
            if S[y, x] and t - last > 6: seeds.append((x, y)); last = t
    loops = []
    cover = []
    for s in seeds:
        # skip seeds already on a found loop
        if any(np.min(np.hypot(P[:, 0] - s[0], P[:, 1] - s[1])) < 5 for P in cover): continue
        r = loop_through(R, cost, c, s, a.win)
        if r is None: continue
        pts, tot = r; P = np.array(pts, float)
        seg = np.linalg.norm(np.diff(P, axis=0), axis=1); Ltot = seg.sum()
        on = R[P[:, 1].astype(int), P[:, 0].astype(int)] >= QTH
        q = float((seg * on[1:]).sum() / max(Ltot, 1))
        # duplicate of an existing loop?
        dup = False
        for l in loops:
            Q = np.array(l['pts'], float)
            d = np.min(np.hypot(P[::10, None, 0] - Q[None, ::5, 0], P[::10, None, 1] - Q[None, ::5, 1]), axis=1)
            if np.mean(d < 6) > 0.8: dup = True; break
        cover.append(P)
        if dup: continue
        loops.append({'id': f"{a.prefix}{len(loops)}", 'seed': list(map(int, s)), 'closed': True, 'pts': [list(p) for p in pts[::3]],
                      'q': round(q, 3), 'len': int(Ltot), 'cost': round(tot, 1)})
        print(loops[-1]['id'], loops[-1]['seed'], 'q', loops[-1]['q'], 'len', loops[-1]['len'])
    json.dump(loops, open(a.out, 'w'))

if __name__ == '__main__':
    main()
