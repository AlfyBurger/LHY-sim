"""First-pass automatic terrain reading of a sector image in the canonical frame.

Proposes per hex: open / woods / heavy_woods (from colour around the centre),
road connections (road colour where hexsides cross), and building candidates
(via trace_buildings colour mask over the whole sector). Output is a DRAFT for
visual checking; borderline hexes are listed under "flags".
usage: auto_sector.py <image> <sector-id> <printing> <out.json>"""
import sys, os, json, cv2, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hexgrid import center, COLS, neighbours

R, HH = 220, 392

def hexes():
    for L in COLS:
        for r in range(1, 14):
            h = f"{L}{r}"; x, y = center(h)
            if y <= 5100:
                yield h, x, y

def patch(hsv, x, y, r):
    x0, y0 = int(max(0, x - r)), int(max(0, y - r))
    p = hsv[y0:int(y + r), x0:int(x + r)]
    yy, xx = np.ogrid[y0:y0 + p.shape[0], x0:x0 + p.shape[1]]
    m = ((xx - x) ** 2 + (yy - y) ** 2 <= r * r) & ((xx - x) ** 2 + (yy - y) ** 2 > 22 * 22)
    return p[m]

def road_mask(hsv, grassV):
    H, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    # tan / pinkish dirt: warmer hue than grass, lower saturation, bright
    return ((H >= 3) & (H <= 24) & (S >= 25) & (S <= 140) & (V >= grassV - 25)).astype(np.uint8)

def main(image, sid, printing, out):
    img = cv2.imread(image)
    if printing == "original":
        # undo the hidden-setup wash
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l = lab[..., 0]; lab[..., 0] = cv2.normalize(l, None, 0, 255, cv2.NORM_MINMAX)
        img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.int16)
    stats = {}
    for h, x, y in hexes():
        p = patch(hsv, x, y, 100)
        stats[h] = (float(np.median(p[:, 0])), float(np.median(p[:, 1])), float(np.median(p[:, 2])), float(np.percentile(p[:, 2], 25)))
    grassV = float(np.median([s[2] for s in stats.values()]))
    result = {"sector": sid, "printing": printing, "status": "auto draft", "default": {"terrain": "open", "level": 0},
              "hexes": {}, "roads_edges": [], "flags": []}
    for h, (Hm, Sm, Vm, V25) in stats.items():
        dv, dv25 = Vm - grassV, V25 - grassV
        if dv < -28 and 22 <= Hm <= 70:
            t = "heavy_woods" if dv25 < -68 else "woods"
            result["hexes"][h] = {"terrain": t}
            if -75 < dv25 < -60: result["flags"].append(f"{h}: woods or heavy woods?")
        elif -28 <= dv < -15:
            result["flags"].append(f"{h}: partly wooded or shaded? (dV {dv:.0f})")
    rm = road_mask(hsv, grassV)
    for h, x, y in hexes():
        for n in neighbours(h):
            if not n or n < h: continue
            nx, ny = center(n)
            if ny > 5100: continue
            mx, my = (x + nx) / 2, (y + ny) / 2
            sub = rm[int(my - 28):int(my + 28), int(mx - 28):int(mx + 28)]
            if sub.size and sub.mean() > 0.30:
                result["roads_edges"].append([h, n, round(float(sub.mean()), 2)])
    result["grassV"] = grassV
    json.dump(result, open(out, "w"), indent=1)
    print(len(result["hexes"]), "wooded hexes;", len(result["roads_edges"]), "road crossings;", len(result["flags"]), "flags")

if __name__ == "__main__":
    main(*sys.argv[1:5])
