# LHY — handoff (21 Nov 2026, updated after the sector 10 south-hill contours)

Handoff for a new chat continuing the work on **/LHY** (The Last Hundred Yards, GMT) and **/wargame-learning**. Read this first, then `docs/stage1.md` (rulings) in the repo.

## 1. The project

- **Two skills to build:**
  - **/LHY**: learn and play The Last Hundred Yards. Claude is opponent (difficulty levels 1–5), teacher and rules referee, and must be able to play either side of any mission.
  - **/wargame-learning**: the general method for learning wargames. It must stay **free of LHY-specific content**. Its working notes are the Project doc `claude/wargame-learning-notes.md` (general lessons only; update it when a general lesson comes up).
- **Stages:** the 5 stages of /boardgame-learning.
  - Stage 2 = one general, mission-independent bot that reads each mission's victory conditions as data.
  - Stage 3 = per-mission tactics and strategy layered on that bot (goal to be reviewed after Stage 2 testing).
- **Scope:** Volume I (missions 1–12) first, then Volume II (13–22) and Mission Pack 1 (23–32). The user owns all three physically, with Volume I in the original 2019 printing.
- **Rules in force:** Series Living Rules v4.4, Errata of 15 Oct 2026, Living Combat Tables of 19 Oct 2026. Optional rules (22.1, 22.2) are out.
- **Play:** on Vassal first, then on the physical copy.

## 2. Where everything is

| What | Where |
|---|---|
| Code, data, rulings, tools | GitHub **AlfyBurger/LHY-sim** (private). Claude may commit and push freely to this repo. |
| This handoff, canonical map images, sector data copies, review images | Mac folder **/Users/Alfy/Desktop/LHY** (see §8). |
| General method notes | Project doc `claude/wargame-learning-notes.md` |
| User-supplied files | Series Living Rules PDF and the LHY Europe Vassal module (v5.0.2). Not in the repo (art and copyright). Ask the user to attach them again if needed. |
| GMT downloads | Listed with URLs in `docs/sources.md`; re-download as needed. Translations and superseded files were deliberately dropped. |

**Repo layout:**
- `docs/stage1.md`: intake, source precedence, rulings R1–R17 and finding F1, open questions Q1–Q6, process log.
- `docs/stage1_inventory.md`: which rules sections Volume I uses, and where each kind of data lives.
- `docs/sources.md`: provenance of every downloaded file.
- `data/tables.json`: combat, terrain, blind hex, stacking, recovery, casualty track, time lapse and fate tables.
- `data/mission_layouts_vol1.json`: sectors, position and rotation per Volume I mission, from the Vassal saves.
- `data/sectors/N_reprint.json` (and paused `N_original.json`): terrain per sector (see §4).
- `data/contour_work/10/`: sector 10 contour tracing state (see §6).
- `tools/`: image and terrain tools. `tools/contour_pipeline.md` describes the contour pipeline.

## 3. How the user wants to work

- **Reviews:**
  - Always show the **plain map side by side** with Claude's reading (never an overlay only), split into north and south halves at a readable size.
  - The user reviews every sector.
  - Reviewing is **tiring** for him. Do extensive self-checking first and send him **only the genuinely doubtful hexes**, marked.
  - Deliver in parts when one part isn't ready, and say plainly why.
- **Commits and skills:** commit and push freely to LHY-sim. Changes to the skills themselves need his review before being saved.
- **General vs specific:** LHY-specific content goes in /LHY and the repo; general lessons go in the wargame-learning notes.
- **Background:** he hasn't played LHY. GMT's documents are the main information source; check every product page, including volumes he doesn't own.
- **Rulings:** record each one in `docs/stage1.md`. Read every hit of a rules search before saying a rule doesn't exist (`src/rules/living.txt` was extracted from the PDF; regenerate it with pdftotext).

## 4. Map data: frame and format

- **Printing:**
  - Work on the **reprint (Vassal) maps only** (R10).
  - The original-printing drafts (sectors 10, 11) are paused. The user will scan his physical maps when back home in France, and the original printing will be redone from those scans.
  - GMT's "Vol. 1 Hidden Setup" sheets show the original printing (F1), but they are too washed out for him to review.
- **Canonical frame** (the GMT hidden-setup image pixels, 3300×5100):
  - Columns A–K, 330 px apart, starting at x = 0.
  - Odd columns (A, C, E, G, I, K): y = 195 + 392·(row−1).
  - Even columns (B, D, F, H, J): y = 391 + 392·(row−1).
  - Row 0 = the north half hexes of the even columns (B0, D0, F0, H0, J0). Half hexes count as full hexes (R6).
  - Hexes are flat-topped, circumradius 220.
  - Helpers in `tools/hexgrid.py`: `center`, `all_hexes`, `neighbours` (order N, NE, SE, S, SW, NW), `to_frame`/`from_frame`.
- **Vassal 5.0.2 sector images:**
  - Landscape 2952×1968, north on the left.
  - Transform: vx = y·227.1/392, vy = 1968 − x·196.44/330.
  - Warped into the frame by `tools/vassal_to_canonical.py`. The results are the 12 images in the Mac folder `maps_reprint_canonical/`.
- **Sector JSON:**
  - `hexes`: per hex, `terrain` (open / woods / heavy woods / river / water…), `level` (hill level: centre dot inside bold contour k), `contour` and `contour_max`, plus bridge/ford flags.
  - `roads`: lists of hex paths; off-map ends are written "@W", "@E", "@N", "@S" (R11).
  - `walls` and `tree_lines`: hexside pairs.
  - `buildings`: kind and traced polygon in frame pixels.
  - Also `scatter`, `open_questions` and `status`.
- **Terrain rulings** (full text in `docs/stage1.md`):
  - Woods: by colour, dark green = heavy (R7); judged at the centre dot, with an edge exception for half hexes (R8).
  - Road hexes keep the terrain beside the road; never judge the road surface at the dot (R15).
  - A fading track is decoration, not road (R11, R13).
  - River hexes are level −1, and a white dot marks a river hex (R12, R14).
  - Water hexes (R16).
  - Hill hex = centre dot inside a bold contour; thin lines don't make hills (R13).
- **Contours (R17 + clarification, confirmed by the user):**
  - `contour` = number of lines (thin or bold) between the centre dot and open ground, counted **all the way out, even through neighbouring hexes**.
  - `contour_max` = highest count inside the hexagon.
  - A bold line has one count along its whole length. On these maps bolds come every 4th line: bold 1 = 4, bold 2 = 8, unless a map shows otherwise.
  - On a saddle, the dot can sit in the neck of a ring shared by two hills (sector 10 F3 = 3).
  - Only the order of counts matters for LOS (4.2.1c–d).
  - Unlisted hexes are 0/0.

## 5. Status by sector (reprint)

| Sector | Terrain (woods, roads, buildings, water, hills) | Contours (dot/max) |
|---|---|---|
| 11 | Reviewed by user 18 Nov, corrections applied | **None on the map**: all hexes 0/0 (checked 21 Nov) |
| 10 | **Confirmed** 19 Nov | North half **confirmed 21 Nov**; south hill **confirmed 21 Nov** |
| 4 | Draft, awaiting review | **In progress** (21 Nov): see §6 'Sector 4 contours' |
| 9 | User review 2 applied; **K12 edge road stub still to confirm** | Not done |
| 12 | **Confirmed** 19 Nov (river level −1, bridges, ford) | Not done (river valley counts downward) |
| 2 | Draft, awaiting review (east-edge road K7–K12 included; K11 woods with road) | Not done |
| 7 | **Confirmed** 19 Nov | **Confirmed** (user corrections 19 Nov) |
| 5 | **Confirmed** 19 Nov | Not done |
| 1, 8, 6, 3 | Not started | Not started |

Order of sectors as the missions use them: 11, 10, 4, 9, 12, 2, 7, 5, 1, 8, 6, 3. Each new sector needs:
1. The automatic first pass (`tools/auto_sector.py`), then a visual check on centre-dot sheets.
2. Buildings traced with seeded GrabCut (`tools/grabcut_buildings.py`).
3. The road audit (`tools/road_audit.py`).
4. A contour pass.
5. The user's review (`tools/review_pair.py` for terrain, `tools/contour_review.py` for contours).

## 6. Contours: method and the sector 10 south hill

**Method.** Reading contours hex by hex by eye failed: lines in hex corners got counted, lines under woods were missed, and reviewing was tiring for the user. The working method traces every line, then computes levels:
1. `tools/line_filter.py <canonical.jpg> resp.png resp.npy 61` builds an oriented dark-thin-line filter (it also saves `resp_ang.npy`). Takes a few minutes; regenerate it rather than storing it.
2. `tools/contour_skeleton.py resp.npy skel.npy` thresholds and skeletonises the response, removes hex-corner marks, labels and dots, and prunes spurs. Sector 10's skeleton is saved as `data/contour_work/10/skeleton.npz` (key `skel`); its border lines were already removed.
3. `tools/line_follow.py resp.npy waypoints.json polylines.json` follows hand-picked lines along the filter response, through gaps under woods, roads, labels and corners. Lines that run close together are better tracked column by column with `tools/column_track.py`. Those tracks are stored as `raw_polylines` in `manual.json`.
4. `tools/contour_close.py skel.npy bridges.json 30 250 50 45 manual.json` closes gaps automatically. `manual.json` holds the polylines, bridges, `cuts` (junk strokes erased: road edges, woods shadows) and `veto` (wrong automatic bridges).
5. `tools/contour_raster.py skel.npy - bridges.json levels.npy levels.png` gives each point the fewest lines crossed to reach open ground. It now uses 1-px barriers (env `CONTOUR_THIN=1`, the default).
6. `tools/contour_hexvalues.py levels.npy skel.npy bridges.json values.json` writes the per-hex dot/max values.
7. Self-checks, all before the user sees anything:
   - `tools/contour_boldcheck.py`: each bold piece must read the same pair (3|4 for bold 1) all the way round.
   - Hexes inside bold k must read above those outside it.
   - `tools/contour_leakscan.py`, `contour_leakpath.py`, `contour_region.py`, `contour_linecomp.py`, `contour_adjwhy.py` and `contour_flat.py` find open or flat lines.
   - `tools/contour_transect.py` prints band levels along a line.
   - `tools/contour_sheet_pts.py` shows the plain map next to the traced lines at given points.
   - `tools/contour_junctions.py` lists places where long lines meet (real contours never meet).
   - Flag dots lying within about 18 px of a line.
8. `tools/contour_review.py` makes the review image: plain map left, lines and dot/max right, doubtful hexes ringed.

`data/contour_work/10/run.sh` chains steps 3–5 (it still uses /tmp paths from the old session: adapt them). The other files in that folder:
- `waypoints.json` and `manual.json`: the hand-traced inputs.
- `raster_values_all.json`: current values for all hexes. The south values in it are wrong.
- `local_values_south_UNRELIABLE.json`: a failed experiment, kept for reference only.

**Typical false lines:** road edges, woods shadows, hex-corner marks, the map border. **Typical missed lines:** two lines so close that the tracing merges them.

**Sector 10 south hill (rows 7–13): confirmed by the user 21 Nov.**
- Values written to `data/sectors/10_reprint.json` (south = hexes with centre y >= 2600). Bold 1 reads 3|4 and bold 2 7|8 all round; summits D9 8, E11 9, F11 9, H11 10 (thin rings inside bold 2). Review images `reviews/review_s10_contours_south_1.jpg` and `_2.jpg` (Mac folder).
- User's answers on the doubtful hexes: I10 1/3 (line through the dot counts downslope, ruling R18), F8 0/2, B12 0/0 (scatter diagram: the junk ring round the white "10" and the digits was cut), C11 max 4, E12 max 7 (a junk loop on the hex-corner mark at its top edge was cut).
- Faults fixed: t3 erased along a hex-corner mark at F12 (waypoints `S_t3_F12hexgap`); t1 merged into bold 1 at the E10 corner (cuts + `raw_polylines.t1_E10bend`) and a false link t2→t1 at (1267–1297, 3733–3745); F11 inner ring opened and bridged to bold 2 (waypoints `S_F11ring_E/W`, veto); junk loops inside the E11 ring (cuts, veto); H11 inner ring's NW arc missing (waypoints `S_H11inner_NW`, cut + veto). The 49 confirmed north values are unchanged.
- `data/contour_work/10/run.sh` now uses `work/s10/` (resp.npy from line_filter.py, ~12 s; skel.npy from skeleton.npz). `raster_values_all.json` holds the current values; `local_values_south_UNRELIABLE.json` is obsolete.
- New method tools and lessons: see the end of `tools/contour_pipeline.md` (band adjacency first: `contour_bandadj.py`, `contour_labview.py`; `contour_ridge.py`, `contour_comp.py`, `contour_ray.py`).

**Sector 4 contours (in progress, 21 Nov).** Work files `data/contour_work/4/` (`run.sh`, `manual.json`, `waypoints.json`, `raster_values_wip.json` = current, unreviewed values). Rebuild: `line_filter.py` -> `contour_skeleton.py` -> `contour_border.py` (new: removes the map border, extends lines that run off the map to the edge) -> `run.sh` (contour_close with CONTOUR_EDGE=3).
- Done: bold height labels bridged (`contour_labelfix.py`), lines hidden under woods or erased along hex-corner marks joined (`contour_gapjoin.py`, `contour_endjoin.py`, each join checked by eye; many automatic proposals were wrong and were rejected), the scatter-diagram digits cut, the three lines converging on the B12 "1"/"2" digits redrawn as separate polylines, the outer south line through the "4" digit, the F11 thin line, the I4 thin line, the H13 line in the woods (L5) and the I12 woods line (A).
- Check: hill levels from the terrain draft (level 1 iff dot >= 4, level 2 iff dot >= 8). Still disagreeing: J2, D6, J7, the J9/I10/J10 hill (reads 2, should be >= 4), D11/C12 and G12/H12 (bold 2 rings read 4-5, should be 8), F12 (draft says not hill, line through the dot: R18 now counts it on the higher side).
- 22 loose line ends remain (`contour_ends.py`, MINRUN 60). Same-level band pairs (`contour_bandadj.py`) list the open lines. North hills (NW B1-E2, NE H2-J4, C6/D5, G7/G8/F8) read mostly right; check them with the bold check before review.

**Contours on the other sectors:** run the same pipeline: 11, 4, 9, 12 (the river valley counts down: river level −1), 2, 5, then the new sectors.

## 7. Remaining Stage 1 work (in order)

1. Contours on 4, 9, 12, 2 and 5 (sectors 10 and 11 done; 11 has no contour lines).
2. User reviews of the sector 4 and 2 drafts; the sector 9 K12 stub.
3. Read sectors 1, 8, 6 and 3 (terrain, road audit, contours).
4. Counter data: transcribe every counter, front and back (values differ squad by squad). Sources: Vassal piece images (front/back per unit) and GMT counter-sheet scans.
5. Mission data for missions 1–12: forces, setup, objectives, MSRs, victory levels, with the errata applied. Mission-specific procedures are listed in `docs/stage1_inventory.md`.
6. Settle open questions Q1–Q6 (`docs/stage1.md`).
7. Rulings quiz (Stage 1 end), then build the /LHY skill draft and the /wargame-learning skill draft (both reviewed by the user before saving).
8. Later: redo the original printing from the user's scans (Volume I is his original 2019 printing; errata differences in R1).

## 8. The Mac folder /Users/Alfy/Desktop/LHY

- `LHY-handoff.md`: this file (also in the repo as `docs/LHY-handoff.md`).
- `maps_reprint_canonical/1.jpg … 12.jpg`: the Vassal reprint sectors warped into the canonical frame. All tools expect these; copy them to `maps/reprint/` in the new workspace. Keep the map images out of the repo while map work is ongoing (user decision, 21 Nov); they may be added once the maps are finished.
- `sector_data/`: copies of `data/sectors/*_reprint.json` as of this handoff. The repo is the master copy.
- `reviews/`: the latest review images per sector. The checked sectors are 7, 10, 11, 12 and 5 (plus the 9 review). Sector 10's contour images are `review_s10_contours_north_*.jpg` (confirmed) and `review_s10_contours_south_*.jpg` (confirmed).

## 9. Mistakes to avoid (from this phase)

- Compare map printings only after putting both on the same hex grid.
- Read every hit of a rules search before saying no rule exists (water hexes: 11.4.11).
- Count lines only inside the hexagon, not in the square crop's corners. Outline hexagons in every crop.
- Don't judge a road hex by the road surface at the centre dot.
- Don't trust a single automatic contour count. Cross-check it against the bold lines and the clear slopes before showing anything.
