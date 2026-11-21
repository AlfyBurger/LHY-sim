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

## Lessons from the sector 10 south hill (21 Nov 2026)

Work dir: `CWORK=work/sN` (resp.npy, skel.npy, bridges.json, levels.npy, barrier.npy); map: `MAP=maps/reprint/N.jpg`.

7. **Band adjacency first** (`contour_bandadj.py`, then `contour_labview.py` to colour the regions with their ids).
   Every band must touch only the bands one level above and below. A band touching a band two levels away, or one
   region that is a different band in two places, pinpoints a merged or missing line far faster than transects.
8. Typical faults found and their fix:
   - a thin line hugging a bold line (10-15 px apart) merges with it in the skeleton: cut the joining stub
     (small `cuts` circles placed off the bold), then draw the thin line as a `raw_polylines` entry measured with
     `contour_ridge.py` (narrow search window, so it cannot jump onto the bold);
   - a line erased where it runs along a hex-corner mark: add `waypoints` across the mark;
   - wrong automatic bridges (to a bold, or reconnecting a cut junk stroke): add the bridge end to `veto`;
   - two candidate branches: compare their line-filter strength along each (the real line is clearly stronger).
9. Checks before review: bold pieces read k-1|k all round (`contour_boldcheck.py`); transects step by one; hill
   level agrees with the dot count (level 1 iff >= 4, level 2 iff >= 8); dots within 18 px of a line looked at one by one
   (most are clear); hex maxima coming from slivers under ~100 px at the hexagon edge flagged as doubtful.
