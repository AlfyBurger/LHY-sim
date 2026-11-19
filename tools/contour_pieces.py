"""Turn a line skeleton into ordered polyline pieces (longest path of each component, spurs dropped),
with an automatic uphill side: the side a piece curves towards; nearly straight pieces copy the side of
the nearest curved, roughly parallel piece. usage: contour_pieces.py skel.npy out.json [minlen]"""
import sys, json, math
import numpy as np, cv2
from collections import deque

def longest_path(pts):
    S = set(pts)
    def far(s):
        dist = {s: 0}; prev = {s: None}; q = deque([s]); last = s
        while q:
            p = q.popleft(); last = p
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    n = (p[0] + dx, p[1] + dy)
                    if n in S and n not in dist: dist[n] = dist[p] + 1; prev[n] = p; q.append(n)
        return last, prev
    a, _ = far(pts[0]); b, prev = far(a)
    path = []; p = b
    while p is not None: path.append(p); p = prev[p]
    return path

def turn_of(P):
    d = np.diff(P, axis=0)
    cr = d[:-1, 0] * d[1:, 1] - d[:-1, 1] * d[1:, 0]; dt = (d[:-1] * d[1:]).sum(1)
    return float(np.degrees(np.arctan2(cr, dt).sum()))

if __name__ == '__main__':
    S = np.load(sys.argv[1]).astype(np.uint8); minlen = float(sys.argv[3]) if len(sys.argv) > 3 else 120
    n, lab = cv2.connectedComponents(S, connectivity=8)
    ys, xs = np.nonzero(S); comp = {}
    for y, x in zip(ys, xs): comp.setdefault(lab[y, x], []).append((int(x), int(y)))
    pieces = []
    for c, pts in comp.items():
        if len(pts) < minlen * 0.8: continue
        path = longest_path(pts)
        P = np.array(path[::4] + ([path[-1]] if (len(path) - 1) % 4 else []), float)
        L = np.linalg.norm(np.diff(P, axis=0), axis=1).sum()
        if L < minlen: continue
        # smooth for turning estimate
        k = 5; Ps = np.array([P[max(0, i - k):i + k + 1].mean(0) for i in range(len(P))])
        pieces.append({'id': f"p{len(pieces)}", 'pts': P.astype(int).tolist(), 'len': round(L), 'turn': round(turn_of(Ps))})
    # uphill side
    for p in pieces:
        p['uphill'] = ('left' if p['turn'] > 0 else 'right') if abs(p['turn']) >= 45 else None
    curved = [p for p in pieces if p['uphill']]
    for p in pieces:
        if p['uphill']: continue
        P = np.array(p['pts'], float); mid = P[len(P) // 2]; d = P[-1] - P[0]; d /= (np.linalg.norm(d) + 1e-9)
        best = None
        for q in curved:
            Q = np.array(q['pts'], float); dist = np.hypot(Q[:, 0] - mid[0], Q[:, 1] - mid[1]); j = int(np.argmin(dist))
            if dist[j] > 150: continue
            j0, j1 = max(j - 3, 0), min(j + 3, len(Q) - 1); e = Q[j1] - Q[j0]; e /= (np.linalg.norm(e) + 1e-9)
            c = float(np.dot(d, e))
            if abs(c) < 0.7: continue
            if best is None or dist[j] < best[0]: best = (dist[j], q, c)
        if best:
            side = best[1]['uphill']
            if best[2] < 0: side = 'right' if side == 'left' else 'left'
            p['uphill'] = side; p['uphill_from'] = best[1]['id']
        else:
            p['uphill'] = 'left' if p['turn'] >= 0 else 'right'; p['uphill_from'] = 'weak'
    json.dump(pieces, open(sys.argv[2], 'w'))
    print(len(pieces), 'pieces;', sum(1 for p in pieces if p.get('uphill_from') == 'weak'), 'weak')
