"""ray.py x0,y0 x1,y1 ... : dark peaks (line filter response) along segments, with traced barrier crossings"""
import sys,numpy as np,cv2
from scipy.signal import find_peaks
from scipy.ndimage import map_coordinates
R=np.load(__import__('os').environ.get('CWORK','work/s10')+'/resp.npy'); B=np.load(__import__('os').environ.get('CWORK','work/s10')+'/barrier.npy'); L=np.load(__import__('os').environ.get('CWORK','work/s10')+'/levels.npy')
for seg in sys.argv[1:]:
    (a,b),(c,d)=[tuple(map(float,p.split(','))) for p in seg.split(':')]
    n=int(np.hypot(c-a,d-b)); t=np.linspace(0,1,n); xs=a+(c-a)*t; ys=b+(d-b)*t
    r=map_coordinates(R,[ys,xs],order=1)
    pk,_=find_peaks(r,height=18,distance=4)
    bb=B[ys.round().astype(int),xs.round().astype(int)]>0
    cr=[]; i=0
    while i<n:
        if bb[i]:
            j=i
            while j<n and bb[j]: j+=1
            k=(i+j)//2; cr.append((int(xs[k]),int(ys[k]))); i=j
        else: i+=1
    lv=[int(L[int(ys[i]),int(xs[i])]) for i in range(0,n,max(1,n//30)) if not bb[i]]
    print(seg); print('  peaks:',[(int(xs[p]),int(ys[p]),int(r[p])) for p in pk]); print('  traced:',cr); print('  lv:',lv)
