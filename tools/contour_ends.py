"""Loose line ends after gap closing (each is a break where bands can leak), drawn over the map.
usage: CWORK=work/sN MAP=maps/reprint/N.jpg contour_ends.py out.jpg [scale] [edge]"""
import os, sys, numpy as np, cv2
from skimage.morphology import skeletonize
W = os.environ.get('CWORK', 'work/s10'); im = cv2.imread(os.environ.get('MAP', 'maps/reprint/10.jpg'))
B = np.load(f'{W}/barrier.npy'); s = float(sys.argv[2]) if len(sys.argv) > 2 else 0.3
e = int(sys.argv[3]) if len(sys.argv) > 3 else 3
S = skeletonize(B > 0).astype(np.uint8); H, Wd = S.shape
nb = cv2.filter2D(S, -1, np.ones((3, 3), np.float32)) * S
def walk(y, x, lim=80):
    seen = {(y, x)}; cur = (y, x)
    for i in range(lim):
        nx = [(cur[0] + dy, cur[1] + dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dy or dx)
              and 0 <= cur[0] + dy < H and 0 <= cur[1] + dx < Wd and S[cur[0] + dy, cur[1] + dx] and (cur[0] + dy, cur[1] + dx) not in seen]
        if len(nx) != 1: return i                  # junction (or other end) reached: a stub
        cur = nx[0]; seen.add(cur)
    return lim
MINRUN = int(__import__('os').environ.get('MINRUN', '60'))
ends = [(int(x), int(y)) for y, x in np.argwhere(nb == 2) if e <= x < Wd - e and e <= y < H - e and walk(y, x) >= MINRUN]
o = (0.55 * im + 0.45 * 255).astype(np.uint8); o[cv2.dilate(S, np.ones((5, 5), np.uint8)) > 0] = (0, 0, 200)
for x, y in ends: cv2.circle(o, (x, y), 22, (255, 0, 0), 6)
cv2.imwrite(sys.argv[1], cv2.resize(o, None, fx=s, fy=s, interpolation=cv2.INTER_AREA))
print(len(ends), 'loose ends'); print(sorted(ends, key=lambda p: (p[1] // 200, p[0])))
