"""Gridded crops of building hexes for placing seed boxes by eye.
Grid lines every 50 canonical px, labelled with absolute coordinates.
usage: building_crops.py <image> <sector.json> <out.jpg>"""
import sys, os, json, cv2, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hexgrid import center
img = cv2.imread(sys.argv[1]); d = json.load(open(sys.argv[2])); tiles = []
for hid, h in d["hexes"].items():
    if not (h.get("building") or h.get("hut")): continue
    x, y = center(hid); x0, y0 = int(x - 250), int(y - 250)
    t = img[max(0, y0):y0 + 500, max(0, x0):x0 + 500].copy()
    t = cv2.copyMakeBorder(t, 0, 500 - t.shape[0], 0, 500 - t.shape[1], cv2.BORDER_CONSTANT)
    for k in range(0, 501, 50):
        gx = (x0 // 50 + 1) * 50 - x0 + k - 50
        gy = (y0 // 50 + 1) * 50 - y0 + k - 50
        if 0 <= gx < 500:
            cv2.line(t, (gx, 0), (gx, 499), (255, 255, 255), 1)
            cv2.putText(t, str(x0 + gx), (gx + 2, 490), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 0, 255), 1)
        if 0 <= gy < 500:
            cv2.line(t, (0, gy), (499, gy), (255, 255, 255), 1)
            cv2.putText(t, str(y0 + gy), (2, gy - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 0, 255), 1)
    cv2.putText(t, hid, (380, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
    tiles.append(t)
while len(tiles) % 3: tiles.append(np.zeros_like(tiles[0]))
cv2.imwrite(sys.argv[3], np.vstack([np.hstack(tiles[i:i + 3]) for i in range(0, len(tiles), 3)]))
