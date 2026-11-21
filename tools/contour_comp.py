"""contour_comp.py x0 y0 x1 y1 out.jpg scale tick: each traced line piece (connected component of the barrier) in its own colour over the line-filter response, to see which pieces join where."""
import sys,cv2,numpy as np
x0,y0,x1,y1=map(int,sys.argv[1:5]); s=float(sys.argv[6]); t=int(sys.argv[7])
R=np.load(__import__('os').environ.get('CWORK','work/s10')+'/resp.npy'); B=np.load(__import__('os').environ.get('CWORK','work/s10')+'/barrier.npy').astype(np.uint8)
sub=B[y0:y1,x0:x1]; n,lab=cv2.connectedComponents(sub,connectivity=8)
r=255-np.clip(R[y0:y1,x0:x1]*3,0,255).astype(np.uint8); r=cv2.cvtColor(r,cv2.COLOR_GRAY2BGR)
r=(0.5*r+127).astype(np.uint8)
pal=[(0,0,255),(0,160,0),(255,0,0),(200,0,200),(0,140,255),(140,90,0),(0,200,200),(90,0,160),(60,60,60)]
for i in range(1,n): r[lab==i]=pal[i%len(pal)]
img=cv2.resize(r,None,fx=s,fy=s,interpolation=cv2.INTER_NEAREST)
for gy in range((y0//t+1)*t,y1,t):
    Y=int((gy-y0)*s); cv2.line(img,(0,Y),(10,Y),(255,0,255),2); cv2.putText(img,str(gy),(12,Y+5),0,0.45,(255,0,255),1)
for gx in range((x0//t+1)*t,x1,t):
    X=int((gx-x0)*s); cv2.line(img,(X,0),(X,10),(255,0,255),2); cv2.putText(img,str(gx),(X-14,24),0,0.45,(255,0,255),1)
cv2.imwrite(sys.argv[5],img)
