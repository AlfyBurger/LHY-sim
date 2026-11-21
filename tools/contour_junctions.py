"""Real contour lines never meet. List skeleton junctions where three or more long branches meet
(two lines merged, or a junk stroke joining two lines) inside a box.
usage: contour_junctions.py skel.npy bridges.json x0 y0 x1 y1 [minbranch]"""
import sys, json, cv2, numpy as np
from skimage.morphology import skeletonize
from skan import Skeleton, summarize
S = np.load(sys.argv[1]).astype(np.uint8); man = json.load(open(sys.argv[2]))
for x, y, r in man.get('cuts', []): cv2.circle(S, (int(x), int(y)), int(r), 0, -1)
for x1, y1, x2, y2 in man['bridges']: cv2.line(S, (x1, y1), (x2, y2), 1, 1)
for pl in man['polylines']: cv2.polylines(S, [np.array(pl, np.int32)], False, 1, 1)
S = skeletonize(cv2.dilate(S, np.ones((3, 3), np.uint8)) > 0)
x0, y0, x1, y1 = map(int, sys.argv[3:7]); mb = float(sys.argv[7]) if len(sys.argv) > 7 else 60
sk = Skeleton(S); df = summarize(sk, separator='_')
deg = {}
for _, r in df.iterrows():
    for end, xc, yc in ((r['node_id_src'], r['image_coord_src_1'], r['image_coord_src_0']), (r['node_id_dst'], r['image_coord_dst_1'], r['image_coord_dst_0'])):
        e = deg.setdefault(end, [int(xc), int(yc), 0, 0]); e[2] += 1
        if r['branch_distance'] >= mb: e[3] += 1
J = [(x, y, d, l) for x, y, d, l in deg.values() if d >= 3 and l >= 3 and x0 <= x < x1 and y0 <= y < y1]
# merge junctions closer than 25 px
out = []
for j in sorted(J):
    if all(abs(j[0] - o[0]) + abs(j[1] - o[1]) > 25 for o in out): out.append(j)
print(len(out), 'junctions'); print(' '.join(f'"{i}:{x},{y}"' for i, (x, y, d, l) in enumerate(out)))
