"""labview.py x0 y0 x1 y1 out.jpg scale — region ids + levels, random colours"""
import sys,cv2,numpy as np
x0,y0,x1,y1=map(int,sys.argv[1:5]); s=float(sys.argv[6])
im=cv2.imread(__import__('os').environ.get('MAP','maps/reprint/10.jpg')); lab=np.load(__import__('os').environ.get('CWORK','work/s10')+'/lab.npy'); L=np.load(__import__('os').environ.get('CWORK','work/s10')+'/levels.npy')
rng=np.random.default_rng(3); pal=rng.integers(60,255,(lab.max()+1,3)).astype(np.uint8); pal[0]=0
c=(0.45*im[y0:y1,x0:x1]+0.55*pal[lab[y0:y1,x0:x1]]).astype(np.uint8); c[lab[y0:y1,x0:x1]==0]=(0,0,0)
c=cv2.resize(c,None,fx=s,fy=s,interpolation=cv2.INTER_AREA)
seen={}
st=int(28/s)
for y in range(y0+5,y1,st):
    for x in range(x0+5,x1,st):
        r=lab[y,x]
        if r==0: continue
        k=(r,(x-x0)//(st*4),(y-y0)//(st*4))
        if k in seen: continue
        seen[k]=1; t=f'{r}:{L[y,x]}'
        cv2.putText(c,t,(int((x-x0)*s),int((y-y0)*s)),0,0.38,(255,255,255),2); cv2.putText(c,t,(int((x-x0)*s),int((y-y0)*s)),0,0.38,(0,0,0),1)
cv2.imwrite(sys.argv[5],c)
