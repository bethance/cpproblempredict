import gzip,json,math,time,urllib.request
C={}
UA="cp-rating-lab"
CF_P="https://codeforces.com/api/problemset.problems"
CF_C="https://codeforces.com/api/contest.list"
AT_M="https://kenkoooo.com/atcoder/resources/problem-models.json"
AT_T="https://kenkoooo.com/atcoder/resources/merged-problems.json"
def get(url,ttl=3600,timeout=30):
 h=C.get(url)
 if h and time.time()-h[0]<ttl:return h[1]
 r=urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":UA,"Accept-Encoding":"gzip"}),timeout=timeout)
 b=r.read()
 if r.headers.get("Content-Encoding")=="gzip":b=gzip.decompress(b)
 d=json.loads(b);C[url]=(time.time(),d)
 return d
def clip(d):return d if d>=400 else 400/math.exp(1-d/400)
