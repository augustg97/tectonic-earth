"""Emulate the shader's fold-coordinate atlas sampling over a lon/lat window, in numpy.

The orogen atlas (README 5.10) is sampled by the shader at (phi, psi), the two
potentials `build_foldphase.py` bakes into `web/fields/*_q.webp`. This draws
the belt patch's height at those coordinates over a window, shaded by the
gate, with the strike field of `_t` as orange ticks -- so a change to the
solver or the encoding can be judged without a browser: the ridges should run
along the ticks, bend with the belt, and keep their 10-18 km spacing.

    python3 emulate_fold.py 0 44 58 26 36 zagros.png     # age lon0 lon1 lat0 lat1 out
"""
import numpy as np, sys, math
from PIL import Image, ImageDraw
HERE=__import__('os').path.dirname(__import__('os').path.abspath(__file__))
ROOT=__import__('os').path.join(HERE,'..')
age=int(sys.argv[1]); lon0,lon1,lat0,lat1=map(float,sys.argv[2:6]); out=sys.argv[6]; Q=64.0
base=f'phan_{age:04d}'
q=np.asarray(Image.open(f'{ROOT}/web/fields/{base}_q.webp').convert('RGBA')).astype(np.float64)
phi=((q[...,0]*256+q[...,1])/65535.0)*2*Q-Q; psi=((q[...,2]*256+q[...,3])/65535.0)*2*Q-Q
t=np.asarray(Image.open(f'{ROOT}/docs/fields/{base}_t.webp').convert('RGB')).astype(np.float64)/255.0
atlas=np.asarray(Image.open(f'{ROOT}/web/atlas.webp').convert('RGB')).astype(np.float64)/255.0; AW=atlas.shape[0]
def patch(px,py,which=0):
    f=np.stack([px-np.floor(px),py-np.floor(py)],-1); cx=which%4; cy=3-which//4
    u=(cx+f[...,0])*0.25; v=(cy+f[...,1])*0.25
    return atlas[((1-v)*(AW-1)).astype(int),(u*(AW-1)).astype(int),0]
kmpx=2.5; latm=math.radians((lat0+lat1)/2)
H,W=q.shape[:2]; Wp=int((lon1-lon0)*111*math.cos(latm)/kmpx); Hp=int((lat1-lat0)*111/kmpx)
LON,LAT=np.meshgrid(np.linspace(lon0,lon1,Wp),np.linspace(lat1,lat0,Hp))
fx=(LON+180)/360*(W-1); fy=(90-LAT)/180*(H-1); x0=np.floor(fx).astype(int); y0=np.floor(fy).astype(int); tx=fx-x0; ty=fy-y0; x1=np.minimum(x0+1,W-1); y1=np.minimum(y0+1,H-1)
bl=lambda a: a[y0,x0]*(1-tx)*(1-ty)+a[y0,x1]*tx*(1-ty)+a[y1,x0]*(1-tx)*ty+a[y1,x1]*tx*ty
P=bl(phi); S=bl(psi); g=np.clip((bl(t[...,0])-0.12)/0.28,0,1)
h=patch(P,S,0); img=(0.25+0.75*h)*(0.3+0.7*g)
im=Image.fromarray((np.stack([img]*3,-1)*255).astype(np.uint8)); d=ImageDraw.Draw(im)
c2=bl(t[...,1])*2-1; s2=bl(t[...,2])*2-1; th=0.5*np.arctan2(s2,c2)
for i in range(12,Hp,28):
    for j in range(12,Wp,28):
        if g[i,j]>0.3: a=th[i,j]; dx,dy=math.cos(a)*10,-math.sin(a)*10; d.line([(j-dx,i-dy),(j+dx,i+dy)],fill=(255,80,40),width=1)
im.save(out); print(out,'phi range',round(float(P.min()),1),round(float(P.max()),1),'psi range',round(float(S.min()),1),round(float(S.max()),1),'gated px',int((g>0.3).sum()))
