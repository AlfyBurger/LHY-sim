"""Prune a line skeleton: repeatedly drop end branches shorter than T px (spurs from woods texture and
hex marks), and drop isolated pieces shorter than M px. usage: skel_prune.py in.npy out.npy [T] [M] [rounds]"""
import sys, numpy as np
from skimage.morphology import skeletonize
from skan import Skeleton, summarize
S = skeletonize(np.load(sys.argv[1]) > 0)
T = float(sys.argv[3]) if len(sys.argv) > 3 else 30; M = float(sys.argv[4]) if len(sys.argv) > 4 else 120
R = int(sys.argv[5]) if len(sys.argv) > 5 else 4
for it in range(R):
    sk = Skeleton(S); df = summarize(sk, separator='_')
    kill = df[((df['branch_type'] == 1) & (df['branch_distance'] < T)) | ((df['branch_type'] == 0) & (df['branch_distance'] < M))]
    if len(kill) == 0: break
    for i in kill.index:
        for (r, c) in sk.path_coordinates(i)[:].astype(int):
            S[r, c] = False
    # restore junction pixels that belonged to surviving branches
    keep = df.drop(kill.index)
    for i in keep.index:
        for (r, c) in sk.path_coordinates(i).astype(int): S[r, c] = True
    S = skeletonize(S)
    print('round', it, 'removed', len(kill))
np.save(sys.argv[2], S)
