#!/bin/sh
# Sector 10 contour chain (steps 3-5 of tools/contour_pipeline.md). Run from the repo root.
# Needs work/s10/resp.npy (tools/line_filter.py maps/reprint/10.jpg work/s10/resp.png work/s10/resp.npy 61)
# and work/s10/skel.npy (from data/contour_work/10/skeleton.npz, key skel).
set -e
D=data/contour_work/10; W=work/s10
python3 tools/line_follow.py $W/resp.npy $D/waypoints.json $W/pl.json > $W/lf.log
python3 - "$D/manual.json" "$W/pl.json" "$W/man.json" <<'PY'
import json, sys
m = json.load(open(sys.argv[1])); pl = json.load(open(sys.argv[2]))
json.dump({'bridges': m.get('bridges', []), 'cuts': m.get('cuts', []), 'veto': m.get('veto', []),
           'polylines': list(pl.values()) + list(m.get('raw_polylines', {}).values())}, open(sys.argv[3], 'w'))
PY
python3 tools/contour_close.py $W/skel.npy $W/bridges.json 30 250 50 45 $W/man.json > $W/close.log
python3 tools/contour_raster.py $W/skel.npy - $W/bridges.json $W/levels.npy $W/levels.png > $W/raster.log
python3 tools/contour_hexvalues.py $W/levels.npy $W/skel.npy $W/bridges.json $W/values.json > $W/hexv.log
