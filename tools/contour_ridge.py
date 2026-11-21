"""ridge.py axis r x,y x,y ... : follow the line-filter ridge near a guide polyline (interpolated);
axis y = line runs roughly N-S (search x per row), x = E-W (search y per column). Prints JSON polyline."""
import sys,json,numpy as np
R=np.load(__import__('os').environ.get('CWORK','work/s10')+'/resp.npy'); ax=sys.argv[1]; r=int(sys.argv[2])
G=np.array([list(map(float,p.split(','))) for p in sys.argv[3:]])
pts=[]
if ax=='y':
    ys=np.arange(int(G[0,1]),int(G[-1,1])+(1 if G[-1,1]>G[0,1] else -1),2 if G[-1,1]>G[0,1] else -2)
    o=np.argsort(G[:,1]); gx=np.interp(ys,G[o,1],G[o,0])
    for y,x in zip(ys,gx):
        a=int(round(x))-r; seg=R[y,a:a+2*r+1]; pts.append([a+int(np.argmax(seg)),int(y)])
else:
    xs=np.arange(int(G[0,0]),int(G[-1,0])+(1 if G[-1,0]>G[0,0] else -1),2 if G[-1,0]>G[0,0] else -2)
    o=np.argsort(G[:,0]); gy=np.interp(xs,G[o,0],G[o,1])
    for x,y in zip(xs,gy):
        a=int(round(y))-r; seg=R[a:a+2*r+1,x]; pts.append([int(x),a+int(np.argmax(seg))])
print(json.dumps(pts))
