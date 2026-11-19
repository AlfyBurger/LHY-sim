"""Contact sheet of map crops around points (plain map left, map + barrier lines right), labelled.
usage: contour_sheet_pts.py skel.npy bridges.json out.jpg "label:x,y" ... [--r 150]"""
import sys, json, cv2, numpy as np
args = [a for a in sys.argv[4:]]; R = 150
if '--r' in args: i = args.index('--r'); R = int(args[i + 1]); del args[i:i + 2]
S = np.load(sys.argv[1]).astype(np.uint8); man = json.load(open(sys.argv[2]))
for x, y, r in man.get('cuts', []): cv2.circle(S, (int(x), int(y)), int(r), 0, -1)
for x1, y1, x2, y2 in man.get('bridges', []): cv2.line(S, (int(x1), int(y1)), (int(x2), int(y2)), 1, 1)
for pl in man.get('polylines', []): cv2.polylines(S, [np.array(pl, np.int32)], False, 1, 1)
im = cv2.imread('/home/claude/maps/reprint/10.jpg'); H, W = S.shape
tiles = []
for a in args:
    lab, xy = a.split(':'); x, y = map(int, xy.split(','))
    x0, y0 = max(x - R, 0), max(y - R, 0); x1, y1 = min(x + R, W), min(y + R, H)
    p = np.full((2 * R, 2 * R, 3), 255, np.uint8); p[y0 - (y - R):y1 - (y - R), x0 - (x - R):x1 - (x - R)] = im[y0:y1, x0:x1]
    q = p.copy(); s = np.zeros((2 * R, 2 * R), np.uint8); s[y0 - (y - R):y1 - (y - R), x0 - (x - R):x1 - (x - R)] = S[y0:y1, x0:x1]
    q[cv2.dilate(s, np.ones((3, 3), np.uint8)) > 0] = (0, 0, 255)
    for t in (p, q):
        cv2.circle(t, (R, R), 10, (255, 0, 255), 2)
        cv2.putText(t, lab, (5, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 4); cv2.putText(t, lab, (5, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    tiles.append(np.hstack([p, np.full((2 * R, 4, 3), 255, np.uint8), q]))
cols = 2; rows = [np.hstack(tiles[i:i + cols] + [np.full_like(tiles[0], 255)] * (cols - len(tiles[i:i + cols]))) for i in range(0, len(tiles), cols)]
out = np.vstack([np.pad(r, ((0, 6), (0, 0), (0, 0)), constant_values=255) for r in rows])
cv2.imwrite(sys.argv[3], out, [cv2.IMWRITE_JPEG_QUALITY, 88])
