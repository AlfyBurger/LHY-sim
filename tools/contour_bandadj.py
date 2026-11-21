"""Band adjacency: lists pairs of free regions that touch across one traced line, with their levels and where.
In a correct trace each band touches only the band one level above and one below; a band touching a band two
levels away marks a merged or missing line. Also saves lab.npy (region ids) for contour_labview.py.
usage: CWORK=work/sN contour_bandadj.py [bridges.json]"""
import sys, json, cv2, numpy as np
from collections import defaultdict
W=__import__('os').environ.get('CWORK','work/s10'); bj=sys.argv[1] if len(sys.argv)>1 else f'{W}/bridges.json'
L=np.load(f'{W}/levels.npy'); S=np.load(f'{W}/skelb.npy' if __import__('os').path.exists(f'{W}/skelb.npy') else f'{W}/skel.npy').astype(np.uint8); man=json.load(open(bj))
for x,y,r in man.get('cuts',[]): cv2.circle(S,(int(x),int(y)),int(r),0,-1)
for x1,y1,x2,y2 in man.get('bridges',[]): cv2.line(S,(int(x1),int(y1)),(int(x2),int(y2)),1,1)
for pl in man.get('polylines',[]): cv2.polylines(S,[np.array(pl,np.int32)],False,1,1)
B=cv2.dilate(S,np.ones((3,3),np.uint8))>0
n,lab=cv2.connectedComponents((~B).astype(np.uint8),connectivity=4)
area=np.bincount(lab.ravel())
ys,xs=np.nonzero(S>0); H,Wd=S.shape
pairs=defaultdict(list)
for dx,dy in ((4,0),(0,4),(3,3),(3,-3)):
    ok=(xs-abs(dx)>=0)&(xs+abs(dx)<Wd)&(ys-abs(dy)>=0)&(ys+abs(dy)<H)
    a=lab[ys[ok]-dy,xs[ok]-dx]; b=lab[ys[ok]+dy,xs[ok]+dx]
    m=(a>0)&(b>0)&(a!=b)
    for p,q,x,y in zip(a[m],b[m],xs[ok][m],ys[ok][m]):
        pairs[(min(p,q),max(p,q))].append((int(x),int(y)))
rep={}
for r in range(1,n):
    if area[r]<2000: continue
    yy,xx=np.nonzero(lab==r) if False else (None,None)
# representative point per region
idx=np.full(n,-1); 
flat=lab.ravel(); order=np.arange(flat.size)
first=np.full(n,-1,np.int64); first[flat[::-1]]=order[::-1]
json.dump({'pairs':{f'{p}-{q}':v for (p,q),v in pairs.items()}},open(f'{W}/adj.json','w'))
np.save(f'{W}/lab.npy',lab)
for (p,q),v in sorted(pairs.items(),key=lambda kv:-len(kv[1])):
    if area[p]<3000 or area[q]<3000 or len(v)<15: continue
    lp=int(L.ravel()[first[p]]); lq=int(L.ravel()[first[q]])
    if max(lp,lq)<3: continue
    v=np.array(v); 
    print(f'{p:>4}(L{lp}) - {q:>4}(L{lq})  n={len(v):5d}  x {v[:,0].min()}-{v[:,0].max()} y {v[:,1].min()}-{v[:,1].max()}')
