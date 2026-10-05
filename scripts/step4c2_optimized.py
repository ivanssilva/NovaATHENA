#!/usr/bin/env python3
"""ATHENA Step 4C.2 optimized Pareto search.
Same scientific question as Step4C.2, with incremental signature coverage,
canonical topology deduplication, and monotonic reuse. Structural only.
"""
import csv,json,collections,itertools
SRC="gt_capacity_benchmark_signature_counts.csv"; KS=(4,5,6); BEAM=160
A=("A0","A1","A2","A3"); C=(("C0A","C0B"),("C1A","C1B")); S=A+tuple(x for p in C for x in p)
LOCAL=frozenset({("C0A","C0B"),("C1A","C1B")}); CANDS=tuple((a,b) for a in S for b in S if a!=b and (a,b) not in LOCAL)
cnt=collections.Counter();seen=set()
with open(SRC,newline="") as f:
 for r in csv.DictReader(f):
  if (r["D"],r["C"])!=("3","8"):continue
  seen.add((r["benchmark"],r["opt"]));n=int(r["occurrences"]);nodes=json.loads(r["signature"])
  keep=[i for i,(op,d) in enumerate(nodes) if not op.startswith("mul")];rem={x:i for i,x in enumerate(keep)}
  nn=[(nodes[x][0],[rem[d] for d in nodes[x][1] if d in rem]) for x in keep]
  if nn:cnt[json.dumps(nn,separators=(",",":"))]+=n
SIG=list(cnt); N=len(SIG); nodes=[json.loads(s) for s in SIG]; weight=[cnt[s]*len(nodes[i]) for i,s in enumerate(SIG)]
perms=[]
for ap in itertools.permutations(A):
 for cp in itertools.permutations((0,1)):
  m=dict(zip(A,ap))
  for old,new in enumerate(cp):m[f"C{old}A"]=f"C{new}A";m[f"C{old}B"]=f"C{new}B"
  perms.append(m)
def canon(extra):return min(tuple(sorted((m[a],m[b]) for a,b in extra)) for m in perms)
def cost(extra):
 ind=collections.Counter(b for a,b in extra);out=collections.Counter(a for a,b in extra)
 return max(ind.values() or [0]),max(out.values() or [0]),sum(max(0,v-1) for v in ind.values())
embcache={}
def emb(i,links):
 key=(i,tuple(sorted(links)))
 if key in embcache:return embcache[key]
 ns=nodes[i]
 if len(ns)>8:embcache[key]=False;return False
 ed=[(d,j) for j,(_,ds) in enumerate(ns) for d in ds];order=sorted(range(len(ns)),key=lambda u:-sum(u in e for e in ed));ass={};used=set()
 def rec(k):
  if k==len(ns):return True
  u=order[k]
  for sl in S:
   if sl in used:continue
   ok=True
   for a,b in ed:
    if a==u and b in ass and (sl,ass[b]) not in links:ok=False;break
    if b==u and a in ass and (ass[a],sl) not in links:ok=False;break
   if ok:
    ass[u]=sl;used.add(sl)
    if rec(k+1):return True
    used.remove(sl);del ass[u]
  return False
 z=rec(0);embcache[key]=z;return z
basecov=frozenset(i for i in range(N) if emb(i,LOCAL))
def sc(cov):return sum(weight[i] for i in cov)
# state=(extra,cov); child only retests signatures not already covered
beam=[(frozenset(),basecov)];levels={}
for k in range(1,7):
 best_by_canon={}
 for extra,cov in beam:
  missing=[i for i in range(N) if i not in cov]
  for e in CANDS:
   if e in extra:continue
   ne=frozenset(set(extra)|{e}); ca=canon(ne)
   if ca in best_by_canon:continue
   links=LOCAL|ne; nc=set(cov)
   for i in missing:
    if emb(i,links):nc.add(i)
   best_by_canon[ca]=(ne,frozenset(nc))
 vals=list(best_by_canon.values())
 vals.sort(key=lambda st:(sc(st[1]),-cost(st[0])[2],-cost(st[0])[0],-cost(st[0])[1]),reverse=True)
 beam=vals[:BEAM];levels[k]=beam
 print("STEP4C2O_LEVEL",k,"unique",len(vals),"beam",len(beam),"best",sc(beam[0][1]),"cache",len(embcache),flush=True)
print("STEP4C2O_AUDIT pairs",len(seen),"signatures",N,"beam",BEAM,"permutations",len(perms),flush=True)
with open("step4c2_optimized_pareto.csv","w",newline="") as f:
 w=csv.writer(f);w.writerow(["K","score","max_fanin","max_fanout","mux_proxy","canonical_links"])
 for k in KS:
  states=levels[k];pareto=[]
  for x,cx in states:
   sx=sc(cx);cc=cost(x)
   dom=False
   for y,cy in states:
    sy=sc(cy);dc=cost(y)
    if sy>=sx and all(a<=b for a,b in zip(dc,cc)) and (sy>sx or dc!=cc):dom=True;break
   if not dom:pareto.append((x,cx))
  pareto.sort(key=lambda st:(-sc(st[1]),cost(st[0]),canon(st[0])))
  print("STEP4C2O_PARETO",k,"count",len(pareto),flush=True)
  for rank,(x,cx) in enumerate(pareto[:20],1):
   ci,co,cm=cost(x);ca=canon(x)
   print("STEP4C2O_CAND",k,rank,"score",sc(cx),"fanin",ci,"fanout",co,"mux",cm,"links",ca,flush=True)
   w.writerow([k,sc(cx),ci,co,cm,json.dumps(ca)])
print("STEP4C2O_LIMITATION constrained beam search, not global-optimum proof; structural metric excludes external operands/liveouts, physical routing/timing/area and temporal performance",flush=True)
