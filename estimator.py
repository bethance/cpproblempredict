import re,urllib.parse,urllib.request
import features as F
import model_runtime as mr
from common import AT_M,CF_C,CF_P,UA,clip,get
def parse(raw):
 raw=raw.strip()
 if not raw:raise ValueError("Paste a problem URL or Codeforces ID.")
 m=None if "://" in raw else re.fullmatch(r"(\d+)([A-Za-z]\d*)",raw)
 if m:return {"p":"cf","cid":int(m[1]),"idx":m[2]}
 u=urllib.parse.urlparse(raw if "://" in raw else "https://"+raw)
 h=u.netloc.lower().split(":")[0]
 if h.endswith("codeforces.com"):
  m=re.search(r"/(?:contest|gym)/(\d+)/problem/([A-Za-z]\d*)",u.path) or re.search(r"/problemset/problem/(\d+)/([A-Za-z]\d*)",u.path)
  if m:return {"p":"cf","cid":int(m[1]),"idx":m[2]}
 if h.endswith("atcoder.jp"):
  m=re.search(r"/contests/([^/]+)/tasks/([^/]+)",u.path)
  if m:return {"p":"at","contest":m[1],"task":m[2]}
 if h.endswith("cses.fi"):
  m=re.search(r"/problemset/task/(\d+)",u.path)
  if m:return {"p":"cses","id":int(m[1])}
 raise ValueError("Unsupported URL. Use a single Codeforces, AtCoder or CSES problem.")
def res(**k):
 d={"official_rating":None,"estimate":None,"low":None,"high":None,"kind":"unavailable","confidence":"Unavailable","tags":[],"model_mae":None}
 d.update(k)
 return d
def cf(p):
 d=get(CF_P)
 if d.get("status")!="OK":raise RuntimeError("Codeforces API error")
 r=d["result"]
 q=next((x for x in r["problems"] if x.get("contestId")==p["cid"] and x.get("index","").upper()==p["idx"].upper()),None)
 if q is None:raise ValueError("Problem not found. It may be a gym or private problem.")
 base=dict(title=q.get("name",""),platform="Codeforces",url="https://codeforces.com/problemset/problem/%d/%s"%(p["cid"],q["index"]),tags=q.get("tags",[]),source="Codeforces API")
 if q.get("rating"):
  v=q["rating"]
  return res(**base,official_rating=v,estimate=v,low=v,high=v,kind="official",confidence="Official",method="Official Codeforces rating",note="Official Codeforces rating.")
 m=mr.cf_model()
 if m is None:return res(**base,method="No model",note="No official rating and no trained model. Run train.py first.")
 row=next((x for x in F.rows(r,get(CF_C).get("result",[])) if x["cid"]==p["cid"] and x["idx"]==q["index"]),None)
 if row is None:return res(**base,method="No data",note="No solve statistics for this problem yet.")
 e,lo,hi=mr.predict(m,row["x"])
 t=m["metrics"]
 low=row["solved"]<100 or row["age"]<.02
 note="No official rating. Ridge + gradient boosting estimate, trained on %d rated problems. Typical error on unseen contests is about %d points; %d%% land within 200."%(t["n_rated_train"],mr.r100(t["mae_blend"]),t["within_200"]*100)
 if low:note+=" Few solves so far, so this is rough."
 return res(**base,estimate=mr.r100(e),low=mr.r100(lo),high=mr.r100(hi),kind="ml_estimate",confidence="Low" if low else "Medium",method="Ridge + gradient boosting",note=note,model_mae=round(t["mae_blend"]))
def at(p):
 url="https://atcoder.jp/contests/%s/tasks/%s"%(urllib.parse.quote(p["contest"],safe=""),urllib.parse.quote(p["task"],safe=""))
 title=p["task"]
 try:
  h=urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":UA}),timeout=10).read().decode("utf-8","ignore")
  m=re.search(r"<title>(.*?)</title>",h,re.I|re.S)
  if m:title=re.sub(r"\s+"," ",re.sub(r"<.*?>","",m[1])).replace(" - AtCoder","").strip()
 except Exception:pass
 base=dict(title=title,platform="AtCoder",url=url,source="AtCoder Problems")
 c=mr.at_map()
 if c is None:return res(**base,method="No map",note="Run train.py to build the AtCoder map.")
 d=get(AT_M).get(p["task"],{}).get("difficulty")
 if d is None:return res(**base,method="No difficulty",note="AtCoder Problems has no difficulty for this task.")
 d=clip(d)
 e,lo,hi=mr.from_atcoder(c,d)
 return res(**base,estimate=mr.r100(e),low=mr.r100(lo),high=mr.r100(hi),kind="ml_estimate",confidence="Approximate",method="Quantile matching",note="AtCoder difficulty is about %d. No problem is rated on both sites, so this is a rough population-level mapping."%round(d))
def cses(p):
 return res(title="CSES task %d"%p["id"],platform="CSES",url="https://cses.fi/problemset/task/%d"%p["id"],confidence="Not available",method="No data",source="CSES",note="CSES publishes no difficulty data.")
def analyze(raw):
 p=parse(raw)
 return {"cf":cf,"at":at,"cses":cses}[p["p"]](p)
