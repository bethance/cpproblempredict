import math,re,time
Y=365.25*24*3600
TAGS=["math","greedy","dp","data structures","brute force","constructive algorithms","graphs","sortings","binary search","dfs and similar","trees","strings","number theory","combinatorics","*special","geometry","bitmasks","two pointers","dsu","shortest paths","probabilities","divide and conquer","hashing","games","matrices","flows","interactive","string suffix structures","graph matchings","fft","ternary search","expression parsing","meet-in-the-middle","2-sat","chinese remainder theorem","schedules"]
KINDS=["div1","div2","div12","div3","div4","edu","global","other"]
NAMES=["log_solved","rel_log_solved","rank_frac","pos","pos_frac","sub","n_problems","log_age","n_tags"]+["kind_"+k for k in KINDS]+["tag_"+t for t in TAGS]
RATED={"div1","div2","div12","div3","div4","edu","global"}
def kind(name):
 n=(name or "").lower()
 if "educational" in n:return "edu"
 if "global round" in n:return "global"
 if re.search(r"div\.?\s*1\s*\+\s*div\.?\s*2",n):return "div12"
 for k in KINDS[:4]:
  if re.search(r"div\.?\s*"+k[-1],n):return k
 return "other"
def idx(s):
 m=re.fullmatch(r"([A-Za-z])(\d*)",s or "")
 return (ord(m[1].upper())-65,int(m[2]) if m[2] else 1) if m else (0,1)
def rows(ps,contests,now=None):
 now=now or time.time()
 meta={c["id"]:c for c in contests}
 sc={(s["contestId"],s["index"]):s.get("solvedCount") for s in ps.get("problemStatistics",[])}
 g={}
 for p in ps["problems"]:
  c=p.get("contestId");s=sc.get((c,p.get("index")))
  if c is None or s is None:continue
  g.setdefault(c,[]).append((p,s))
 out=[]
 for c,it in g.items():
  m=meta.get(c,{})
  k=kind(m.get("name",""))
  t=m.get("startTimeSeconds")
  age=max((now-t)/Y,0.0) if t else 3.0
  pos=[idx(p["index"])[0] for p,_ in it]
  mp=max(pos)
  n=len(set(pos))
  top=max(s for _,s in it)
  rk={p["index"]:i for i,(p,_) in enumerate(sorted(it,key=lambda z:-z[1]))}
  for p,s in it:
   a,b=idx(p["index"]);tg=p.get("tags",[])
   x=[math.log1p(s),math.log((s+1)/(top+1)),rk[p["index"]]/(len(it)-1) if len(it)>1 else .5,a,a/mp if mp>0 else 0.0,b,n,math.log(age+.1),len(tg)]
   x+=[float(k==q) for q in KINDS]
   x+=[float(q in tg) for q in TAGS]
   out.append({"cid":c,"idx":p["index"],"name":p.get("name",""),"rating":p.get("rating"),"tags":tg,"kind":k,"solved":s,"age":age,"x":x})
 return out
