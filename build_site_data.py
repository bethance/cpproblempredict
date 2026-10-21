import argparse,json
from datetime import datetime,timezone
from pathlib import Path
import features as F
import model_runtime as mr
from common import AT_M,AT_T,CF_C,CF_P,clip,get
OUT=Path(__file__).with_name("site")/"data.json"
def load(name,url,cd):
 f=Path(cd)/name if cd else None
 if f and f.exists():return json.loads(f.read_text(encoding="utf-8"))
 d=get(url,0,120)
 if f:
  f.parent.mkdir(parents=True,exist_ok=True)
  f.write_text(json.dumps(d),encoding="utf-8")
 return d
if __name__=="__main__":
 ap=argparse.ArgumentParser()
 ap.add_argument("--cache-dir")
 cd=ap.parse_args().cache_dir
 m,c=mr.cf_model(),mr.at_map()
 if m is None:raise SystemExit("no model, run train.py first")
 ps=load("cf_problemset.json",CF_P,cd)["result"]
 cs=load("cf_contests.json",CF_C,cd)["result"]
 cf={}
 for r in F.rows(ps,cs):
  t=", ".join(r["tags"]);v=r["rating"]
  if v:cf["%d%s"%(r["cid"],r["idx"])]=[r["name"],v,v,v,v,t,r["solved"]]
  else:
   e,lo,hi=mr.predict(m,r["x"])
   cf["%d%s"%(r["cid"],r["idx"])]=[r["name"],None,mr.r100(e),mr.r100(lo),mr.r100(hi),t,r["solved"]]
 at={}
 if c:
  ms=load("atcoder_models.json",AT_M,cd)
  tt={p["id"]:p.get("title") or p["id"] for p in load("atcoder_merged.json",AT_T,cd)}
  for k,v in ms.items():
   d=v.get("difficulty")
   if d is None:continue
   d=clip(d)
   e,lo,hi=mr.from_atcoder(c,d)
   at[k.lower()]=[tt.get(k,k),round(d),mr.r100(e),mr.r100(lo),mr.r100(hi)]
 t=m["metrics"]
 data={"generated":datetime.now(timezone.utc).strftime("%Y-%m-%d"),"model":{"mae":round(t["mae_blend"]),"within_200":round(t["within_200"],2),"n_train":t["n_rated_train"]},"cf":cf,"at":at}
 OUT.parent.mkdir(exist_ok=True)
 OUT.write_text(json.dumps(data,separators=(",",":"),ensure_ascii=False),encoding="utf-8")
 print("wrote",OUT,len(cf),"codeforces,",len(at),"atcoder,",OUT.stat().st_size//1024,"KB")
