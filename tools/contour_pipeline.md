# Contour pipeline (per sector)

1. `work/linefilt.py <canonical.jpg> resp.png resp.npy 61` - oriented dark-thin-line filter (saves `resp_ang.npy`).
2. `tools/contour_skeleton.py resp.npy skel.npy` - hysteresis + skeleton, hex-grid marks removed, spurs pruned.
3. `tools/line_follow.py resp.npy data/contour_work/N/waypoints.json polylines.json` - hand-picked lines
   (gaps under woods, roads, labels, hex vertices) followed along the filter response.
4. `tools/contour_close.py skel.npy bridges.json 30 250 50 45 manual.json` - auto gap closing
   (manual.json = polylines + manual bridges + cuts of junk + vetoed auto bridges).
5. `tools/contour_raster.py skel.npy - bridges.json levels.npy levels.png` - level of every point = least
   number of lines crossed to reach open ground; per hex: level at the dot, highest level inside the hexagon.
6. Checks: `contour_leakscan.py` (neighbouring bands that are one region = open line),
   `contour_leakpath.py` / `contour_region.py` / `contour_linecomp.py` (where a line is open),
   `contour_transect.py` (band levels on a transect), `contour_adjwhy.py` (why a band has its level),
   `contour_sheet_pts.py` (plain map vs traced lines at given points), and the confirmed hill hexes
   (inside a bold line) as a cross-check: every hex inside bold k must be above every hex outside it.
