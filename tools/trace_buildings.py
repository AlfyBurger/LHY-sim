"""Trace building footprints in a GMT hidden-setup sector image.

Searches only the hexes listed as having buildings (and their immediate surroundings),
masks out printed hex labels and vertex marks, classifies roof/stone/hut/shadowed-roof
pixels by colour, and returns simplified polygons in image pixel coordinates.
usage: trace_buildings.py <sector.json> <image> <out.json> [preview.jpg]"""
import sys, os, json, cv2, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hexgrid import center, COLS
R, HH = 220, 392

def hexpoly(x, y, k=1.0):
    return np.array([(x+R*k, y), (x+R/2*k, y+HH/2*k), (x-R/2*k, y+HH/2*k), (x-R*k, y), (x-R/2*k, y-HH/2*k), (x+R/2*k, y-HH/2*k)], np.int32)

def mask_pixels(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    H, S, V = (hsv[..., i].astype(int) for i in range(3))
    roof = ((H <= 20) | (H >= 165)) & (S > 60) & (V < 220) & (V > 35)
    stone = (S < 50) & (V > 50) & (V < 180)
    hut = (H >= 10) & (H <= 28) & (S > 95) & (V > 140)
    dark = (V < 125) & ~((H >= 26) & (H <= 95) & (S > 40))     # shadowed roofs, not dark foliage
    m = (roof | stone | hut | dark).astype(np.uint8) * 255
    # remove printed labels, centre dots and vertex marks
    for L in COLS:
        for r in range(1, 14):
            x, y = center(f"{L}{r}")
            cv2.rectangle(m, (int(x-120), int(y-205)), (int(x+120), int(y-95)), 0, -1)
            cv2.circle(m, (int(x), int(y)), 14, 0, -1)
            for vx, vy in hexpoly(x, y):
                cv2.circle(m, (int(vx), int(vy)), 30, 0, -1)
    return m

def trace(sector_json, image):
    d = json.load(open(sector_json)); img = cv2.imread(image); m = mask_pixels(img)
    region = np.zeros(m.shape, np.uint8)
    for hid, h in d["hexes"].items():
        if h.get("building") or h.get("hut"):
            cv2.fillPoly(region, [hexpoly(*center(hid), 1.15)], 255)
    m &= region
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((21, 21), np.uint8))
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    polys = []
    for c in cs:
        a = cv2.contourArea(c)
        if a < 900: continue
        p = cv2.approxPolyDP(c, 6, True).reshape(-1, 2).tolist()
        polys.append({"area": int(a), "poly": p})
    return img, polys

def preview(img, polys, sector_json, out):
    d = json.load(open(sector_json)); vis = img.copy(); tiles = []
    for p in polys:
        cv2.polylines(vis, [np.array(p["poly"], np.int32)], True, (255, 0, 255), 5)
    for hid, h in d["hexes"].items():
        if h.get("building") or h.get("hut"):
            x, y = center(hid); x0, y0 = max(0, int(x-260)), max(0, int(y-260))
            t = vis[y0:y0+520, x0:x0+520].copy()
            t = cv2.copyMakeBorder(t, 0, 520-t.shape[0], 0, 520-t.shape[1], cv2.BORDER_CONSTANT)
            cv2.putText(t, hid, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 0, 255), 4)
            tiles.append(t)
    while len(tiles) % 4: tiles.append(np.zeros_like(tiles[0]))
    rows = [np.hstack(tiles[i:i+4]) for i in range(0, len(tiles), 4)]
    cv2.imwrite(out, np.vstack(rows))

if __name__ == '__main__':
    img, polys = trace(sys.argv[1], sys.argv[2])
    json.dump(polys, open(sys.argv[3], 'w'))
    if len(sys.argv) > 4: preview(img, polys, sys.argv[1], sys.argv[4])
    print(len(polys), "polygons")
