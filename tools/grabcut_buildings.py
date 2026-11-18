"""Refine building outlines with GrabCut from seed boxes.
Seeds: a JSON list of {"hex":..,"box":[x0,y0,x1,y1]} in canonical pixels (one per building).
usage: grabcut_buildings.py <image> <seeds.json> <out.json> [preview.jpg]"""
import sys, json, cv2, numpy as np
def refine(img, box, pad=45):
    x0, y0, x1, y1 = [int(v) for v in box]
    X0, Y0 = max(0, x0 - pad), max(0, y0 - pad); X1, Y1 = min(img.shape[1], x1 + pad), min(img.shape[0], y1 + pad)
    sub = img[Y0:Y1, X0:X1]
    mask = np.zeros(sub.shape[:2], np.uint8)
    rect = (x0 - X0, y0 - Y0, x1 - x0, y1 - y0)
    bgd, fgd = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    cv2.grabCut(sub, mask, rect, bgd, fgd, 6, cv2.GC_INIT_WITH_RECT)
    fg = np.where((mask == 1) | (mask == 3), 255, 0).astype(np.uint8)
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
    cs, _ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cs: return None
    c = max(cs, key=cv2.contourArea)
    p = cv2.approxPolyDP(c, 5, True).reshape(-1, 2) + [X0, Y0]
    return p.tolist()
if __name__ == '__main__':
    img = cv2.imread(sys.argv[1]); seeds = json.load(open(sys.argv[2])); out = []
    for s in seeds:
        p = refine(img, s["box"])
        if p: out.append({"hex": s["hex"], "poly": p})
    json.dump(out, open(sys.argv[3], "w"))
    if len(sys.argv) > 4:
        vis = img.copy(); tiles = []
        for b in out:
            cv2.polylines(vis, [np.array(b["poly"], np.int32)], True, (255, 0, 255), 4)
        for b in out:
            x, y = np.mean(b["poly"], 0).astype(int); t = vis[max(0, y-160):y+160, max(0, x-160):x+160].copy()
            t = cv2.copyMakeBorder(t, 0, 320-t.shape[0], 0, 320-t.shape[1], cv2.BORDER_CONSTANT)
            cv2.putText(t, b["hex"], (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3); tiles.append(t)
        while len(tiles) % 6: tiles.append(np.zeros_like(tiles[0]))
        cv2.imwrite(sys.argv[4], np.vstack([np.hstack(tiles[i:i+6]) for i in range(0, len(tiles), 6)]))
    print(len(out), "outlines")
