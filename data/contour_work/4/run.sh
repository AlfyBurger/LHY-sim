#!/bin/sh
# Sector 4 contour chain. Run from the repo root. Needs work/s4/resp.npy and work/s4/skelb.npy:
#   python3 tools/line_filter.py maps/reprint/4.jpg work/s4/resp.png work/s4/resp.npy 61
#   python3 tools/contour_skeleton.py work/s4/resp.npy work/s4/skel.npy
#   python3 tools/contour_border.py work/s4/skel.npy work/s4/skelb.npy
set -e
D=data/contour_work/4; W=work/s4
python3 tools/line_follow.py $W/resp.npy $D/waypoints.json $W/pl.json > $W/lf.log
python3 - "$D/manual.json" "$W/pl.json" "$W/man.json" <<'PY'
import json, sys
m = json.load(open(sys.argv[1])); pl = json.load(open(sys.argv[2]))
json.dump({'bridges': m.get('bridges', []), 'cuts': m.get('cuts', []), 'veto': m.get('veto', []),
           'polylines': list(pl.values()) + list(m.get('raw_polylines', {}).values())}, open(sys.argv[3], 'w'))
PY
CONTOUR_EDGE=3 python3 tools/contour_close.py $W/skelb.npy $W/bridges.json 30 250 50 45 $W/man.json > $W/close.log
python3 tools/contour_raster.py $W/skelb.npy - $W/bridges.json $W/levels.npy $W/levels.png 1650 1250 > $W/raster.log
python3 tools/contour_hexvalues.py $W/levels.npy $W/skelb.npy $W/bridges.json $W/values.json > $W/hexv.log
