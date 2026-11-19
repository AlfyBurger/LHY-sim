"""Contour count per hex (dot level and highest level inside the hexagon) from traced contour polylines.

Each traced line knows its uphill side: the side it curves towards (lines around hills), or the side
given explicitly. Crossing a line along a straight segment changes the level by +1 (going uphill) or -1.
Dot levels are solved by walking the hex graph from a hex known to be at level 0; every hex pair is then
re-checked, and pairs whose crossings disagree with the solved levels are reported (usually a gap in a
traced line, a missed line or a spurious one).

usage: contour_levels.py lines.json zero_hex out.json [render_bg out.png]
lines.json: [{"pts": [[x,y],...], "closed": bool, "uphill": "auto"|"left"|"right", "id": str?}, ...]
"""
import sys, json, math
import numpy as np
from collections import deque
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from hexgrid import all_hexes, center, neighbours

R_HEX = 220.0

def load_lines(path):
    L = json.load(open(path)); out = []
    for i, l in enumerate(L):
        P = np.array(l['pts'], float)
        if l.get('closed') and np.linalg.norm(P[0] - P[-1]) > 0.5: P = np.vstack([P, P[:1]])
        # simplify: keep every point at least 4 px from the previous kept one
        keep = [0]
        for j in range(1, len(P)):
            if np.linalg.norm(P[j] - P[keep[-1]]) >= 4: keep.append(j)
        if keep[-1] != len(P) - 1: keep.append(len(P) - 1)
        P = P[keep]
        d = np.diff(P, axis=0)
        cr = d[:-1, 0] * d[1:, 1] - d[:-1, 1] * d[1:, 0]
        dt = d[:-1, 0] * d[1:, 0] + d[:-1, 1] * d[1:, 1]
        turn = float(np.arctan2(cr, dt).sum())
        up = l.get('uphill', 'auto')
        s = (1 if turn > 0 else -1) if up == 'auto' else (1 if up == 'left' else -1)
        # 'left' here means the side where cross(direction, v) > 0 in image coordinates
        out.append({'id': l.get('id', str(i)), 'P': P, 'A': P[:-1], 'B': P[1:], 's': s, 'turn': math.degrees(turn),
                    'bb': (P[:, 0].min(), P[:, 1].min(), P[:, 0].max(), P[:, 1].max())})
    return out

def crossings(lines, p, q):
    """Signed crossings along segment p->q: list of (t, sign, line id)."""
    p = np.asarray(p, float); q = np.asarray(q, float); r = q - p; res = []
    x0, x1 = min(p[0], q[0]), max(p[0], q[0]); y0, y1 = min(p[1], q[1]), max(p[1], q[1])
    for l in lines:
        bx0, by0, bx1, by1 = l['bb']
        if bx1 < x0 or bx0 > x1 or by1 < y0 or by0 > y1: continue
        A, B = l['A'], l['B']; s = B - A
        den = r[0] * s[:, 1] - r[1] * s[:, 0]
        ok = np.abs(den) > 1e-9
        ap = A - p
        t = np.where(ok, (ap[:, 0] * s[:, 1] - ap[:, 1] * s[:, 0]) / np.where(ok, den, 1), -1)
        u = np.where(ok, (ap[:, 0] * r[1] - ap[:, 1] * r[0]) / np.where(ok, den, 1), -1)
        hit = ok & (t >= 0) & (t < 1) & (u >= 0) & (u < 1)
        for k in np.nonzero(hit)[0]:
            c = s[k, 0] * r[1] - s[k, 1] * r[0]          # cross(line dir, segment dir)
            res.append((float(t[k]), (1 if c > 0 else -1) * l['s'], l['id']))
    res.sort()
    return res

def solve(lines, zero_hex):
    H = [h for h in all_hexes()]
    lev = {zero_hex: 0}; q = deque([zero_hex]); via = {}
    while q:
        h = q.popleft()
        for n in neighbours(h):
            if n is None or n in lev: continue
            c = crossings(lines, center(h), center(n))
            lev[n] = lev[h] + sum(x[1] for x in c); via[n] = h; q.append(n)
    bad = []
    seen = set()
    for h in H:
        for n in neighbours(h):
            if n is None or (n, h) in seen: continue
            seen.add((h, n))
            c = crossings(lines, center(h), center(n))
            d = sum(x[1] for x in c)
            if lev[h] + d != lev[n]:
                bad.append((h, n, lev[h], lev[n], [(round(t, 2), sg, i) for t, sg, i in c]))
    return lev, bad

def hex_max(lines, h, dot_level, step=14):
    cx, cy = center(h); best = dot_level; where = (cx, cy)
    for yy in np.arange(cy - 190, cy + 191, step):
        for xx in np.arange(cx - R_HEX + 10, cx + R_HEX - 9, step):
            # inside flat-topped hexagon (shrunk 6 px)
            dx, dy = abs(xx - cx), abs(yy - cy)
            # flat-topped hexagon: |y| <= h, |x| <= R - |y|/sqrt(3); shrink 6 px
            if dy > 196 - 6 or dx > (R_HEX - 6) - dy / math.sqrt(3):
                continue
            if not (0 <= xx <= 3300 and 0 <= yy <= 5100): continue
            v = dot_level + sum(x[1] for x in crossings(lines, (cx, cy), (xx, yy)))
            if v > best: best = v; where = (xx, yy)
    return best, where

if __name__ == '__main__':
    lines = load_lines(sys.argv[1]); zero = sys.argv[2]
    lev, bad = solve(lines, zero)
    res = {}
    for h in all_hexes():
        mx, w = hex_max(lines, h, lev[h])
        res[h] = {'contour': lev[h], 'contour_max': mx}
    json.dump({'hexes': res, 'inconsistent_pairs': bad, 'turns': {l['id']: round(l['turn']) for l in lines}},
              open(sys.argv[3], 'w'), indent=1)
    print('inconsistent pairs:', len(bad))
    for b in bad: print(' ', b)
    if len(sys.argv) > 5:
        import cv2
        bg = cv2.imread(sys.argv[4]); bg = (0.55 * bg + 0.45 * 255).astype(np.uint8)
        for l in lines:
            P = l['P'].astype(np.int32)
            cv2.polylines(bg, [P], False, (0, 0, 200), 3)
            # uphill tick marks
            for j in range(0, len(P) - 1, 25):
                d = (P[j + 1] - P[j]).astype(float); d /= (np.linalg.norm(d) + 1e-9)
                nrm = np.array([-d[1], d[0]]) * l['s']   # side where cross(d, v) > 0 -> (-dy, dx)
                e = (P[j] + nrm * 18).astype(int)
                cv2.line(bg, tuple(int(v) for v in P[j]), tuple(int(v) for v in e), (0, 0, 200), 3)
        for (a, b, *_rest) in bad:
            cv2.line(bg, tuple(int(v) for v in center(a)), tuple(int(v) for v in center(b)), (255, 0, 255), 6)
        for h, v in res.items():
            x, y = center(h); x, y = int(x), int(y)
            cv2.circle(bg, (x, y), 9, (0, 0, 0), -1)
            t = f"{h} {v['contour']}/{v['contour_max']}"
            cv2.putText(bg, t, (x - 85, y + 52), cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 8)
            cv2.putText(bg, t, (x - 85, y + 52), cv2.FONT_HERSHEY_SIMPLEX, 1.25, (0, 0, 0), 3)
        cv2.imwrite(sys.argv[5], bg)
