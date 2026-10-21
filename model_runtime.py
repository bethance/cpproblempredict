import bisect,json
from pathlib import Path
D=Path(__file__).with_name("model")
L={}
def load(name):
 p=D/name
 if not p.exists():return None
 t=p.stat().st_mtime
 if name in L and L[name][0]==t:return L[name][1]
 d=json.loads(p.read_text(encoding="utf-8"));L[name]=(t,d)
 return d
def cf_model():return load("cf_model.json")
def at_map():return load("atcoder_map.json")
def walk(t,x):
 n=0
 while t["l"][n]!=-1:n=t["l"][n] if x[t["f"][n]]<=t["t"][n] else t["r"][n]
 return t["v"][n]
def clamp(v):return min(3500.0,max(800.0,v))
def predict(m,x):
 z=[(v-a)/s for v,a,s in zip(x,m["mean"],m["std"])]
 r=m["ridge"]["intercept"]+sum(c*v for c,v in zip(m["ridge"]["coef"],z))
 g=m["gbr"]
 b=g["init"]+g["lr"]*sum(walk(t,x) for t in g["trees"])
 p=m["blend_w"]*b+(1-m["blend_w"])*r
 return clamp(p),clamp(p+m["interval"]["lo"]),clamp(p+m["interval"]["hi"])
def interp(d,xs,ys):
 if d<=xs[0]:return ys[0]+d-xs[0]
 if d>=xs[-1]:return ys[-1]+d-xs[-1]
 i=bisect.bisect_right(xs,d)
 if xs[i]==xs[i-1]:return ys[i-1]
 return ys[i-1]+(ys[i]-ys[i-1])*(d-xs[i-1])/(xs[i]-xs[i-1])
def from_atcoder(c,d):
 a=interp(d,c["atcoder"],c["cf_all"]);b=interp(d,c["atcoder"],c["cf_div2"])
 return clamp((a+b)/2),clamp(min(a,b)-c["margin"]),clamp(max(a,b)+c["margin"])
def r100(v):return int(round(v/100)*100)
