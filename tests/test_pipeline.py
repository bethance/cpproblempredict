import json,math,random,shutil,subprocess,sys,tempfile,time
from pathlib import Path
R=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(R))
import features as F
random.seed(1)
NOW=time.time()
def fake_cf():
 names=["Codeforces Round {} (Div. 2)","Codeforces Round {} (Div. 1)","Educational Codeforces Round {}","Codeforces Round {} (Div. 3)","Codeforces Global Round {}"]
 cs,ps,st=[],[],[]
 eff={t:random.uniform(-80,80) for t in F.TAGS}
 for c in range(1,1201):
  nm=random.choice(names).format(c)
  t=NOW-(1201-c)*5*86400
  cs.append({"id":c,"name":nm,"startTimeSeconds":int(t),"phase":"FINISHED"})
  age=(NOW-t)/F.Y
  for i in range(random.choice([5,6,7,8])):
   base=800+i*random.uniform(250,380)+(300 if "Div. 1" in nm else 0)
   tg=random.sample(F.TAGS,random.randint(1,4))
   r=int(min(3500,max(800,round((base+sum(eff[x] for x in tg)*.3+random.gauss(0,60))/100)*100)))
   s=max(0,int(math.exp(10.5-r/330+.25*math.log(age+.5)+random.gauss(0,.35))))
   ix=chr(65+i)
   ps.append({"contestId":c,"index":ix,"name":"P%d%s"%(c,ix),"tags":tg,**({"rating":r} if c<=1150 else {})})
   st.append({"contestId":c,"index":ix,"solvedCount":s})
 return {"status":"OK","result":{"problems":ps,"problemStatistics":st}},{"status":"OK","result":cs}
def fake_at():
 ms,mg=({},[])
 for i in range(1500):
  k="abc%d_%s"%(100+i//6,"abcdef"[i%6])
  ms[k]={"difficulty":random.gauss(300+(i%6)*280,200)}
  mg.append({"id":k,"contest_id":k.split("_")[0],"title":"Task "+k})
 return ms,mg
def main():
 tmp=Path(tempfile.mkdtemp())
 cp,cc=fake_cf()
 am,ag=fake_at()
 for n,d in [("cf_problemset",cp),("cf_contests",cc),("atcoder_models",am),("atcoder_merged",ag)]:(tmp/(n+".json")).write_text(json.dumps(d))
 md=R/"model"
 bk={p.name:p.read_bytes() for p in md.glob("*.json")}
 try:
  subprocess.run([sys.executable,str(R/"train.py"),"--cache-dir",str(tmp)],check=True)
  import model_runtime as mr
  import estimator as es
  from common import AT_M,CF_C,CF_P
  m=mr.cf_model()
  rated=[r for r in F.rows(cp["result"],cc["result"]) if r["rating"]][:300]
  err=[abs(mr.predict(m,r["x"])[0]-r["rating"]) for r in rated]
  assert sum(err)/len(err)<250
  print("in-sample mae",round(sum(err)/len(err)))
  tb={CF_P:cp,CF_C:cc,AT_M:am}
  es.get=lambda u,**k:tb[u]
  o=es.analyze("1A")
  assert o["kind"]=="official" and o["estimate"]==o["official_rating"]
  u=es.analyze("https://codeforces.com/problemset/problem/1190/D")
  assert u["kind"]=="ml_estimate" and u["low"]<=u["estimate"]<=u["high"],u
  a=es.analyze("https://atcoder.jp/contests/abc100/tasks/abc100_a")
  h=es.analyze("https://atcoder.jp/contests/abc116/tasks/abc116_f")
  assert a["low"]<=a["estimate"]<=a["high"] and h["estimate"]>=a["estimate"]
  assert es.analyze("https://cses.fi/problemset/task/1068")["kind"]=="unavailable"
  subprocess.run([sys.executable,str(R/"build_site_data.py"),"--cache-dir",str(tmp)],check=True)
  s=json.loads((R/"site"/"data.json").read_text())
  assert s["cf"]["1A"][1] and s["cf"]["1190D"][1] is None and s["cf"]["1190D"][2] and "abc100_a" in s["at"]
  js="const L=require('./site/logic.js'),d=require('./site/data.json');if(L.parseInput('https://codeforces.com/contest/1/problem/A').key!=='1A')throw 1;if(L.parseInput('https://atcoder.jp/contests/abc100/tasks/abc100_a').key!=='abc100_a')throw 2;if(L.parseInput('1190d').key!=='1190D')throw 3;if(L.parseInput('hello world')!==null)throw 4;const r=L.describe(d,L.parseInput('1190D'));if(!r.value||!r.notes.length)throw 5;if(!L.describe(d,L.parseInput('1A')).value)throw 6;if(!L.describe(d,L.parseInput('abc100_a')).value)throw 7;if(!L.describe(d,L.parseInput('https://cses.fi/problemset/task/1068')).error)throw 8;console.log('site ok')"
  p=subprocess.run(["node","-e",js],cwd=R,capture_output=True,text=True)
  print(p.stdout.strip(),p.stderr.strip())
  assert p.returncode==0
  print("all checks passed")
 finally:
  (R/"site"/"data.json").unlink(missing_ok=True)
  for p in md.glob("*.json"):p.unlink()
  for n,d in bk.items():(md/n).write_bytes(d)
  shutil.rmtree(tmp,ignore_errors=True)
if __name__=="__main__":main()
