"""Follow contour lines on a skeleton of the map's dark thin lines, from one seed point per line.

The skeleton comes from an oriented line filter (see work notes) thresholded with hysteresis; hex-grid
vertex marks ("tripods"), hex labels and centre dots are erased first. From each seed the tracer walks
the skeleton both ways, taking the straightest branch at junctions and jumping gaps (up to MAXGAP px,
within +-35 deg of the current heading). A trace closes when it comes back to its start.

usage: contour_trace.py skel.npy seeds.json out.json
seeds.json: {"name": [x, y], ...}   or {"name": {"seed": [x,y], "maxgap": 80}}
"""
import sys, json, math
import numpy as np

MAXGAP = 70

def nbrs(S, p):
    x, y = p; out = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if (dx or dy) and S[y + dy, x + dx]: out.append((x + dx, y + dy))
    return out

def heading(path, k=12):
    a = np.array(path[max(0, len(path) - 1 - k)], float); b = np.array(path[-1], float)
    v = b - a; n = np.linalg.norm(v); return v / n if n > 0 else None

def ahead(S, p, q, visited, k=8):
    """Direction of the branch starting p->q, following it greedily k steps."""
    cur, prev = q, p; seen = {p, q}
    for _ in range(k):
        nx = [n for n in nbrs(S, cur) if n not in seen and n not in visited]
        if not nx: break
        prev, cur = cur, nx[0]; seen.add(cur)
    v = np.array(cur, float) - np.array(p, float); n = np.linalg.norm(v)
    return v / n if n > 0 else None

def walk(S, start, d0, start_set, maxgap):
    path = [start]; visited = {start}; H, W = S.shape
    d = d0
    for it in range(40000):
        p = path[-1]
        if not (3 <= p[0] < W - 3 and 3 <= p[1] < H - 3): return path, 'edge'
        if len(path) > 120 and math.hypot(p[0] - start[0], p[1] - start[1]) < 10: return path, 'closed'
        hd = heading(path) if len(path) > 4 else d
        if hd is None: hd = d
        cands = [n for n in nbrs(S, p) if n not in visited]
        if cands:
            best = None
            for n in cands:
                v = ahead(S, p, n, visited)
                if v is None: v = np.array(n, float) - np.array(p, float); v /= np.linalg.norm(v)
                c = float(np.dot(v, hd))
                if best is None or c > best[0]: best = (c, n)
            if best[0] > math.cos(math.radians(70)):
                path.append(best[1]); visited.add(best[1]); continue
        # gap jump: search a cone ahead
        found = None
        x0, y0 = p
        R = maxgap
        ys, xs = np.nonzero(S[max(0, y0 - R):y0 + R + 1, max(0, x0 - R):x0 + R + 1])
        xs = xs + max(0, x0 - R); ys = ys + max(0, y0 - R)
        v = np.stack([xs - x0, ys - y0], 1).astype(float); dist = np.linalg.norm(v, axis=1)
        ok = (dist >= 3) & (dist <= R)
        if ok.any():
            cosang = (v[ok] @ hd) / dist[ok]
            cand = np.nonzero(ok)[0]
            good = cosang > math.cos(math.radians(35))
            best = None
            for j, c in zip(cand[good], cosang[good]):
                q = (int(xs[j]), int(ys[j]))
                if q in visited and not (q in start_set and len(path) > 120): continue
                score = dist[j] * (1 + 3 * (1 - c))
                if best is None or score < best[0]: best = (score, q)
            if best: found = best[1]
        if found is None: return path, 'open'
        # straight bridge
        n = int(math.hypot(found[0] - x0, found[1] - y0))
        for t in range(1, n + 1):
            q = (int(round(x0 + (found[0] - x0) * t / n)), int(round(y0 + (found[1] - y0) * t / n)))
            if q not in visited: path.append(q); visited.add(q)
        if found in start_set and len(path) > 120: return path, 'closed'
    return path, 'max'

def trace(S, seed, maxgap=MAXGAP):
    x, y = int(seed[0]), int(seed[1])
    ys, xs = np.nonzero(S[y - 15:y + 16, x - 15:x + 16])
    if len(xs) == 0: return None
    j = np.argmin((xs - 15) ** 2 + (ys - 15) ** 2); s = (int(x - 15 + xs[j]), int(y - 15 + ys[j]))
    n = nbrs(S, s)
    if not n: return None
    d = np.array(n[0], float) - np.array(s, float); d /= np.linalg.norm(d)
    start_set = {(s[0] + dx, s[1] + dy) for dx in range(-6, 7) for dy in range(-6, 7)}
    f, st = walk(S, s, d, start_set, maxgap)
    if st == 'closed': return {'closed': True, 'pts': [list(p) for p in f], 'status': st}
    b, st2 = walk(S, s, -d, set(f[:40]) | start_set, maxgap)
    pts = [list(p) for p in b[::-1]] + [list(p) for p in f[1:]]
    return {'closed': False, 'pts': pts, 'status': f'{st2}|{st}'}

if __name__ == '__main__':
    S = np.load(sys.argv[1]).astype(bool)
    seeds = json.load(open(sys.argv[2])); out = {}
    for name, s in seeds.items():
        if isinstance(s, dict): r = trace(S, s['seed'], s.get('maxgap', MAXGAP))
        else: r = trace(S, s)
        if r is None: print(name, 'no skeleton near seed'); continue
        out[name] = {'closed': r['closed'], 'pts': r['pts'][::3]}
        print(name, r['status'], len(r['pts']))
    json.dump(out, open(sys.argv[3], 'w'))
