"""Warp a Vassal 5.0.2 sector image (landscape, north left) into the canonical frame
(GMT hidden-setup layout: portrait 3300x5100, row 1 north, column A west).
usage: vassal_to_canonical.py <vassal.jpg> <out.jpg>"""
import sys, os, cv2, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hexgrid import VASSAL_SX, VASSAL_SY, VASSAL_H
src = cv2.imread(sys.argv[1])
# canonical (x, y) -> vassal (vx, vy) = (y*SX, H - x*SY); build the inverse map for remap
xs, ys = np.meshgrid(np.arange(3300, dtype=np.float32), np.arange(5100, dtype=np.float32))
mapx = ys * VASSAL_SX
mapy = VASSAL_H - xs * VASSAL_SY
out = cv2.remap(src, mapx, mapy, cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
cv2.imwrite(sys.argv[2], out, [cv2.IMWRITE_JPEG_QUALITY, 92])
