"""Oriented line filter: response = mean(side bands) - mean(centre line) over length L, max over angle.
usage: linefilt.py img out.png resp.npy [L]"""
import sys, math, cv2, numpy as np
im = cv2.imread(sys.argv[1]); g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32)
L = int(sys.argv[4]) if len(sys.argv) > 4 else 61
best = np.full(g.shape, -1e9, np.float32); ang = np.zeros(g.shape, np.uint8)
K = L + 20
for i, th in enumerate(np.arange(0, 180, 6)):
    c = np.zeros((K, K), np.float32); s = np.zeros((K, K), np.float32)
    t = math.radians(th); dx, dy = math.cos(t), math.sin(t); nx, ny = -dy, dx
    o = K // 2
    for u in np.linspace(-L / 2, L / 2, L * 2):
        for w in (-1, 0, 1):
            x, y = o + u * dx + w * 0.7 * nx, o + u * dy + w * 0.7 * ny
            c[int(round(y)), int(round(x))] = 1
        for w in (-8, -7, 7, 8):
            x, y = o + u * dx + w * nx, o + u * dy + w * ny
            s[int(round(y)), int(round(x))] = 1
    k = s / s.sum() - c / c.sum()
    r = cv2.filter2D(g, -1, k)
    m = r > best; best[m] = r[m]; ang[m] = i
np.save(sys.argv[3], best); np.save(sys.argv[3].replace(".npy","_ang.npy"), ang)
v = np.clip(best * 4, 0, 255).astype(np.uint8)
cv2.imwrite(sys.argv[2], 255 - v)
print(np.percentile(best, [50, 90, 99, 99.9]))
