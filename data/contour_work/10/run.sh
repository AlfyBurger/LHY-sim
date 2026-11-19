set -e
python3 lhy-sim/tools/line_follow.py /tmp/lf10.npy /tmp/wp10.json /tmp/pl10.json > /tmp/lf.log
python3 - <<'PY'
import json
pl = json.load(open('/tmp/pl10.json')); m = json.load(open('/tmp/manual_extra.json')) if __import__('os').path.exists('/tmp/manual_extra.json') else {}
json.dump({'bridges': m.get('bridges', []), 'cuts': m.get('cuts', []), 'veto': m.get('veto', []), 'polylines': list(pl.values()) + list(m.get('raw_polylines', {}).values())}, open('/tmp/man10.json','w'))
PY
python3 lhy-sim/tools/contour_close.py /tmp/sk4.npy /tmp/bcm.json 30 250 50 45 /tmp/man10.json
python3 lhy-sim/tools/contour_raster.py /tmp/sk4.npy - /tmp/bcm.json /tmp/LM.npy /tmp/LM.png
python3 work/evalW.py /tmp/LM.npy
