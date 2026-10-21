import argparse,json,time
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor as GB
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold
import features as F
from common import AT_M,AT_T,CF_C,CF_P,clip,get
OUT=Path(__file__).with_name("model")
GP=dict(n_estimators=300,learning_rate=.05,max_depth=3,subsample=.8,min_samples_leaf=10,random_state=0)
def now():return datetime.now(timezone.utc).isoformat(timespec="seconds")
def load(name,url,cd):
 f=Path(cd)/name if cd else None
 if f and f.exists():return json.loads(f.read_text(encoding="utf-8"))
 print("downloading",url)
 d=get(url,0,120)
 if f:
  f.parent.mkdir(parents=True,exist_ok=True)
  f.write_text(json.dumps(d),encoding="utf-8")
 return d
def mae(a,b):return float(np.mean(np.abs(a-b)))
def scale(X):
 m=X.mean(0);s=X.std(0);s[s<1e-9]=1.0
 return m,s
def folds(X,y,g):
 al=[.1,1,10,100,300]
 r={a:np.zeros(len(y)) for a in al}
 b=np.zeros(len(y))
 for i,(tr,te) in enumerate(GroupKFold(5).split(X,y,g)):
  print("fold",i+1,"of 5")
  m,s=scale(X[tr])
  A,B=(X[tr]-m)/s,(X[te]-m)/s
  for a in al:r[a][te]=Ridge(alpha=a).fit(A,y[tr]).predict(B)
  b[te]=GB(**GP).fit(X[tr],y[tr]).predict(X[te])
 return r,b
def tree(e):
 t=e.tree_
 f=lambda v:[round(float(i),6) for i in v]
 return {"l":t.children_left.tolist(),"r":t.children_right.tolist(),"f":t.feature.tolist(),"t":f(t.threshold),"v":f(t.value[:,0,0])}
def train_cf(cd):
 ps=load("cf_problemset.json",CF_P,cd)["result"]
 cs=load("cf_contests.json",CF_C,cd)["result"]
 allr=F.rows(ps,cs)
 rated=[r for r in allr if r["rating"]]
 print(len(allr),"problems,",len(rated),"rated,",len({r["cid"] for r in rated}),"contests")
 if len(rated)<500:raise SystemExit("not enough rated problems to train")
 X=np.array([r["x"] for r in rated],dtype=float)
 y=np.array([r["rating"] for r in rated],dtype=float)
 g=np.array([r["cid"] for r in rated])
 ro,go=folds(X,y,g)
 ba=min(ro,key=lambda a:mae(y,ro[a]))
 ra=ro[ba]
 bw,bm=0.0,None
 for w in np.linspace(0,1,11):
  e=mae(y,w*go+(1-w)*ra)
  if bm is None or e<bm:bw,bm=float(w),e
 res=y-(bw*go+(1-bw)*ra)
 lo,hi=np.quantile(res,[.1,.9])
 ug=np.unique(g)
 np.random.default_rng(0).shuffle(ug)
 half=set(ug[:len(ug)//2].tolist())
 ina=np.array([c in half for c in g])
 a,b=np.quantile(res[ina],[.1,.9])
 cov=float(np.mean((res[~ina]>=a)&(res[~ina]<=b)))
 mt={"n_rated_train":len(y),"mae_constant_baseline":mae(y,np.full_like(y,np.median(y))),"mae_ridge":mae(y,ra),"ridge_alpha":ba,"mae_gbr":mae(y,go),"mae_blend":bm,"rmse_blend":float(np.sqrt(np.mean(res**2))),"within_100":float(np.mean(np.abs(res)<=100)),"within_200":float(np.mean(np.abs(res)<=200)),"interval_level":.8,"interval_heldout_coverage":cov}
 print(json.dumps(mt,indent=2))
 m,s=scale(X)
 rm=Ridge(alpha=ba).fit((X-m)/s,y)
 gm=GB(**GP).fit(X,y)
 model={"version":1,"trained_at":now(),"feature_names":F.NAMES,"mean":m.tolist(),"std":s.tolist(),"ridge":{"coef":rm.coef_.tolist(),"intercept":float(rm.intercept_)},"gbr":{"init":float(gm.init_.constant_.ravel()[0]),"lr":GP["learning_rate"],"trees":[tree(e[0]) for e in gm.estimators_]},"blend_w":bw,"interval":{"lo":float(lo),"hi":float(hi),"level":.8},"metrics":mt}
 (OUT/"cf_model.json").write_text(json.dumps(model,separators=(",",":")),encoding="utf-8")
 top=np.argsort(-np.abs(rm.coef_))[:8]
 print("top ridge weights:",[(F.NAMES[i],round(float(rm.coef_[i]),1)) for i in top])
 return rated
def train_at(rated,cd):
 ms=load("atcoder_models.json",AT_M,cd)
 mg=load("atcoder_merged.json",AT_T,cd)
 cid={p["id"]:p.get("contest_id","") for p in mg}
 at=[clip(m["difficulty"]) for k,m in ms.items() if m.get("difficulty") is not None and not m.get("is_experimental") and cid.get(k,"").startswith(("abc","arc","agc"))]
 if len(at)<300:
  print("not enough atcoder problems, skipping")
  return
 a=[r["rating"] for r in rated if r["kind"] in F.RATED]
 b=[r["rating"] for r in rated if r["kind"] in {"div2","div3","div4","edu"}]
 q=np.linspace(.02,.98,49)
 qs=lambda v:[round(float(i),1) for i in np.maximum.accumulate(np.quantile(v,q))]
 out={"quantiles":q.round(3).tolist(),"atcoder":qs(at),"cf_all":qs(a),"cf_div2":qs(b),"margin":100,"n_atcoder":len(at),"n_cf_all":len(a),"n_cf_div2":len(b),"trained_at":now()}
 (OUT/"atcoder_map.json").write_text(json.dumps(out),encoding="utf-8")
 print("atcoder map saved from",len(at),"problems")
if __name__=="__main__":
 ap=argparse.ArgumentParser()
 ap.add_argument("--cache-dir")
 a=ap.parse_args()
 OUT.mkdir(exist_ok=True)
 t=time.time()
 train_at(train_cf(a.cache_dir),a.cache_dir)
 print("done in %ds"%(time.time()-t))
