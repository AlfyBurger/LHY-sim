# LHY — Stage 1 record

## Intake (2026-11-18)

- **Owned:** Volume I, Volume II, Mission Pack 1 (physical; counters cut).
- **Scope:** Volume I (missions 1–12) first; Volume II (13–22) and Mission Pack 1 (23–32) added later.
- **Rules in force:** Series Living Rules v4.4 (19 Oct 2026), Counter/Mission Errata (15 Oct 2026), Living Combat Tables (19 Oct 2026). These override the printed books in the boxes (older printings).
- **Optional rules (22.1 Command & Control, 22.2 Skin in the Game):** out for now; may be added later as game settings.
- **Play:** Vassal first, then the physical copy.
- **Claude's roles:** opponent (difficulty levels 1–5), teacher (learning mode), rules referee.
- **Sides:** Claude must be able to play either side of any mission.
- **Architecture goal (to review after Stage 2 testing):** Stage 2 = one general bot, mission-independent code reading each mission's victory conditions as data; Stage 3 = tactics and strategy per mission, layered on the general bot.

## Source precedence

User rulings > Errata (15 Oct 2026) > Living Rules v4.4 and Living Combat Tables > Series Playbook examples > mission cards and Vassal module > fan sources.

## Rulings

- R1 (user, 2026-11-18): Volume I is the **original 2019 printing**. Apply the errata entries for the original module (Mission 2 sector, sector 9 hex B11 building absent, Mission 8 objective wording as printed for the original sector 11). Map images from Vassal/GMT are presumed reprint: check sectors 9 and 11 against photos of the user's maps.
- R2 (user): Terrain read from images is checked by the user on colour overlays, sector by sector.
- R4 (user): Line of sight by shape: building footprints and contour lines are traced from the map images and LOS is computed geometrically; lines passing within a small tolerance of a shape are flagged for a ruling. Forest (hex-based, 4.2.1a) and walls/tree lines (hexsides) stay hex-based.
- R5 (user): Both printings are encoded: original (user's copy; provisional until checked against the physical maps) and reprint (Vassal 5.0.2, GMT Basic Training 2023). Order: sectors as missions use them (11, 10, 4, 9, 12, 2, 7, 5, 1, 8, 6, 3).
- F1 (finding, 2026-11-18): GMT's "Vol. 1 Hidden Setup" sector images are the ORIGINAL printing (sector 9 hex B11 has no building). The Vassal module 5.0.2 sector images are the REPRINT (B11 building present). Corrected after aligning both on one grid: sector 11 differs only in additions (building B1, edge woods, road stubs); sector 2 differs substantially (reprint adds three roads, buildings, marsh). A January 2019 playbook diagram of sector 5 matches the original (no western road branch).
- R3 (user): The engine implements the rules Volume I missions use first; the skill's rules text covers all series rules.

## Open questions

Each with Claude's current reading (not settled).

- Q1 Mortar Fire Action Table: 76–82mm section MDRM count "3" is printed in red (red = negative on LHY charts). Reading: 3 markers, red is a highlight of a changed value.
- Q2 AVM table: LATW/FT vs FP, towed gun, urban building or urban road is printed "1/2". Reading: +1 for one of LATW/FT, +2 if both? or +1 LATW / +2 FT? To settle from rules 14.2e and the playbook.
- Q3 Terrain table: rural/urban, wheeled vehicles "2/1". Reading: 2 MP rural, 1 MP urban.
- Q4 Playbook examples use terms and numbers older than v4.4 ("Encirclement" marker = Envelopment; "Obscure Target" DRM, no longer on the charts; 11.4.8g, 13.6.3.1b). Reading: follow v4.4 rules and charts; use the examples only where they agree.
- Q5 Game Track is v5.1.2023 while rules are v4.4 (2026): check the Clean-Up Phase step order and the Fate table against the rules.
- Q6 Sector 11 terrain questions: see data/sectors/11.json "open_questions".

## Process log

- Sources: every GMT product page checked, including volumes not owned (they carry extra documents: LOS examples, bonus missions, design articles). Two files removed from GMT's server; both superseded. Translations and superseded files deleted.
- Terrain method (sector 11 pilot): automatic first pass for woods (colour at hex centre) and road crossings (colour at hexside midpoints), then visual check and correction; buildings located by eye as seed boxes on gridded crops, outlines traced with GrabCut on the sharper reprint art and reused for the original where the art is identical.
- Mistake: compared the Vassal map before rotating it into the hex frame and over-stated the differences between printings. Always align both images on the same grid before comparing.
