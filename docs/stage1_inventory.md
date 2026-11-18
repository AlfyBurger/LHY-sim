# LHY — Stage 1.3 inventory: procedures vs data

Scope: Volume I (missions 1–12). Rules: Series Rules v4.4, Errata 15 Oct 2026, Combat Tables 19 Oct 2026, Game Track v5.1.2023.

## 1. Rules sections Volume I needs

| Needed for Volume I | Not used by Volume I missions (later: Vol II, MP1, other volumes) |
|---|---|
| 1–3 counters, units, stacking, force organization | 4.1.8.1 Hedgerows, 4.1.9.1.1 Sunken Roads (MP1 by MSR) |
| 4 terrain, LOS, blind hexes, concealment (incl. rivers, bridges, fords: M5, M7) | 4.1.13–4.1.15, 4.1.18 marsh, beach, palm/brush, gullies (check per sector) |
| 5–9 sequence, activation, coordination, ad hoc, reaction, mandatory actions | 15.2 Russian/Japanese, 15.2.2 Russian command |
| 10 maneuver incl. vehicles, transport (M12 riders/passengers), assaults | 16 Airborne landings (Vol II) |
| 11 fire: enfilade, small arms, mortars (60mm, 8cm, 81mm platoon), anti-tank | 17 Night/Twilight (Vol II missions) |
| 12 recovery, rally, heroism, shock | 19 Mines and wire |
| 13–14 fire and assault resolution | 20.8 Dummies (no Vol I MSR allows them) |
| 15.1 Elite (check per mission) | 22 Optional rules (out by intake) |
| 18 Random events | 23 Design Your Own |
| 20 setup: random draw, hidden placement, offboard entry, CO tanks (M5, M12) | |
| 21 winning: control, final score, victory level | |

Mission-specific procedures in Volume I that go beyond the series rules: simultaneous secret setup (M2, M4), road-hex victory count (M2), MOP counting (M3, M4, M8), delayed and low-ammo mortars (M4, M9, M10), secret reserve entry hex and timed release (M11), concealment-marker draw system for the defender (M12).

## 2. Where each kind of data lives

| Component | Data to capture | Where it lives | State |
|---|---|---|---|
| Map sectors 1–12 | per hex: terrain type, level, hill hex (centre dot inside bold contour), contour elevation (thin contours), buildings (stone/wooden/urban/hut), roads/paths/railroads and their connections, river/bridge/ford; per hexside: wall, tree line; half hexes; scatter diagram | Images only: Vassal sector images (v2) and GMT "Vol. 1 Hidden Setup" sector images, which print the ID in every hex | **To digitise** — the largest data job |
| Mission map layouts | sectors, position, rotation (rev = 180°) | Vassal mission saves (decoded) | Extracted for M1–M12 |
| Missions | forces, setup, objectives, CDL, initiative and coordination DRMs, MSRs, victory levels | Mission sheet PDF (2020, text), Vassal mission card images, Errata | Text available; errata to apply |
| Counters | per counter: nationality, company, platoon, unit ID, cohesion, SAV and range (underscored or not), ATV and range, AV, AEV, assault value, MV, steps, elite; back side (disrupted / shocked / reduced) | Images only: Vassal per-counter images (front and back, named by unit) and GMT counter-sheet scans (fronts of US 1F, GE 2F) | **To transcribe** — values differ squad by squad |
| Combat tables | assault resolution, AVM, small arms / AT / mortar DRMs, mortar fire action, vehicle destruction, fire resolution, minefield | Combat Tables PDF (text extracts badly; image readable) | To transcribe and check against rules text |
| Terrain effects, blind hex, stacking, MP allowance, recovery, shock tables | as above | Combat Tables p.2 (image) | To transcribe |
| Game track | casualty track with casualty points, time track, random event and fate tables, coordination, time lapse, mortar boxes | Game Track PDF (image only) | To transcribe |
| Unit capability table, vehicle maneuver matrix | which unit may do which action | Rules p.42–43 (text garbled) | To transcribe from rendered pages |
| Markers | DRM markers, motion, overwatch, assault, concealment, etc. | Rules | State only, no data |

## 3. Self-tests available

- Playbook 24.x rule examples (terrain/LOS, activation, withdrawal, overrun, shoot & scoot, halt & fire, enfilade, fire resolution, assaults, mortars) — diagram-based, need rendering.
- Playbook 25.1 and 25.2 extended examples (infantry and mortars; armor).
- LOS Examples PDF (May 2021, 8 pages of diagrams).
- Basic Training booklet (sectors 2, 4, 11, 12).

Already noticed for step 1.5: some playbook examples cite old rule numbers or terms ("Encirclement" marker, "Obscure Target" DRM, 11.4.8g, 13.6.3.1b) that no longer match v4.4.

## 4. Printing-dependent data (Volume I)

The errata distinguishes the original Volume I from the reprint: Mission 2 sector number (10 vs 11), a building in sector 9 hex B11 (absent in the original; excluded from M4 MOP), Mission 8 objective (10 of 13 vs 11 of 13 building points with the reprint's sector 11). Fortified Position SAV range is no longer underscored (counter errata). The Vassal module and GMT sector images are presumably the reprint.
