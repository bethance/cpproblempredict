(function(root){
function parseInput(raw){
 raw=(raw||"").trim()
 if(!raw)return null
 let m=raw.match(/^(\d+)\s*([A-Za-z]\d?)$/)
 if(m)return{site:"cf",key:m[1]+m[2].toUpperCase()}
 if(/^[a-z]+\d+_[a-z0-9]+$/i.test(raw))return{site:"at",key:raw.toLowerCase()}
 let u
 try{u=new URL(/^https?:\/\//i.test(raw)?raw:"https://"+raw)}catch(e){return null}
 const h=u.hostname.toLowerCase(),p=u.pathname
 if(h.endsWith("codeforces.com")){
  m=p.match(/\/(?:contest|gym)\/(\d+)\/problem\/([A-Za-z]\d?)/)||p.match(/\/problemset\/problem\/(\d+)\/([A-Za-z]\d?)/)
  if(m)return{site:"cf",key:m[1]+m[2].toUpperCase()}
 }
 if(h.endsWith("atcoder.jp")){
  m=p.match(/\/contests\/[^/]+\/tasks\/([^/]+)/)
  if(m)return{site:"at",key:decodeURIComponent(m[1]).toLowerCase()}
 }
 if(h.endsWith("cses.fi")&&/\/problemset\/task\/\d+/.test(p))return{site:"cses"}
 return null
}
function describe(d,q){
 if(!q)return{error:"That doesn't look like a Codeforces or AtCoder problem. Try 1850A, or paste a link."}
 if(q.site=="cses")return{error:"CSES doesn't publish difficulty data, so I can't say much about this one."}
 const notes=[]
 if(q.site=="cf"){
  const r=d.cf[q.key]
  if(!r)return{error:"I couldn't find that Codeforces problem. It may be brand new, or from a gym or private contest."}
  const[title,off,est,lo,hi,tags,solved]=r,m=q.key.match(/^(\d+)(.+)$/)
  const url="https://codeforces.com/problemset/problem/"+m[1]+"/"+m[2]
  if(off)return{title,before:"Codeforces rates this one",value:""+off,after:".",notes,tags,url}
  notes.push("This is a machine-learning guess. On problems it hadn't seen, it was usually off by about "+d.model.mae+" points.")
  if(solved<100)notes.push("Very few people have solved it so far, so take it with extra salt.")
  return{title,before:"There's no official rating yet. My best guess is about",value:""+est,after:", probably between "+lo+" and "+hi+".",notes,tags,url}
 }
 const r=d.at[q.key]
 if(!r)return{error:"I couldn't find an AtCoder difficulty for that task. It may be too new, or not rated."}
 const[title,diff,est,lo,hi]=r
 notes.push("AtCoder and Codeforces ratings aren't directly comparable, and no problem is rated on both. Treat this as a rough guide.")
 return{title,before:"AtCoder's difficulty here is about "+diff+", which lands around",value:""+est,after:" on the Codeforces scale (roughly "+lo+" to "+hi+").",notes,tags:"",url:"https://atcoder.jp/contests/"+q.key.split("_")[0]+"/tasks/"+q.key}
}
const api={parseInput,describe}
if(typeof module!=="undefined")module.exports=api;else root.RatingLogic=api
})(this)
