"""Full-resolution map tile for reading waypoints: hex outlines and ids, faint 100 px grid with labels on
the borders, optional traced lines overlaid. usage: trace_tile.py img x0 y0 x1 y1 out.jpg [lines.json] [scale]"""
import sys, json, math, cv2, numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from hexgrid import all_hexes, center
im = cv2.imread(sys.argv[1]); x0, y0, x1, y1 = map(int, sys.argv[2:6]); out = sys.argv[6]
args = [a for a in sys.argv if a != '--light']
lines = json.load(open(args[7])) if len(args) > 7 and args[7] != '-' else {}
sc = float(args[8]) if len(args) > 8 else 1.0
o = im.copy() if '--light' not in sys.argv else (0.55 * im + 0.45 * 255).astype(np.uint8)
for h in all_hexes():
    x, y = center(h)
    pts = np.array([(int(x + 220 * math.cos(math.radians(60 * k))), int(y + 220 * math.sin(math.radians(60 * k)))) for k in range(6)])
    cv2.polylines(o, [pts], True, (230, 200, 120), 1)
    cv2.circle(o, (int(x), int(y)), 7, (0, 0, 255), -1)
    cv2.putText(o, h, (int(x) + 10, int(y) + 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
pal = [(255, 0, 255), (0, 120, 255), (255, 80, 0), (0, 200, 0), (200, 0, 120), (0, 200, 200)]
items = lines.items() if isinstance(lines, dict) else enumerate(lines)
for i, (k, l) in enumerate(items):
    c = pal[i % len(pal)]
    cv2.polylines(o, [np.array(l['pts'], np.int32)], l.get('closed', False), c, 2)
    p = l['pts'][len(l['pts']) // 3]
    cv2.putText(o, str(k), (p[0] + 4, p[1] - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.8, c, 2)
c = o[y0:y1, x0:x1].copy()
ov = c.copy()
for x in range((x0 // 100 + 1) * 100, x1, 100):
    cv2.line(ov, (x - x0, 0), (x - x0, y1 - y0), (255, 255, 255), 1)
    cv2.putText(c, str(x), (x - x0 + 2, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 4)
    cv2.putText(c, str(x), (x - x0 + 2, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (160, 0, 0), 2)
for y in range((y0 // 100 + 1) * 100, y1, 100):
    cv2.line(ov, (0, y - y0), (x1 - x0, y - y0), (255, 255, 255), 1)
    cv2.putText(c, str(y), (2, y - y0 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 4)
    cv2.putText(c, str(y), (2, y - y0 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (160, 0, 0), 2)
c = cv2.addWeighted(c, 0.8, ov, 0.2, 0)
if sc != 1: c = cv2.resize(c, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
cv2.imwrite(out, c, [cv2.IMWRITE_JPEG_QUALITY, 92])
