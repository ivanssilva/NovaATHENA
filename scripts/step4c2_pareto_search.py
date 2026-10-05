#!/usr/bin/env python3
"""ATHENA Step 4C.2: constrained alternative-topology search around K=4,5,6.
Beam search over directed sparse links; deduplicates slot-label isomorphisms
(4 simple ALUs interchangeable; 2 C2 pairs interchangeable), and reports
Pareto candidates for structural score versus fan-in/fan-out/mux proxy.
Structural only; no timing/cycles/IPC/speedup.
"""
import csv,json,collections,itertools
SRC="gt_capacity_benchmark_signature_counts.csv"; KS=(4,5,6); BEAM=300
A=("A0","A1","A2","A3"); C=(("C0A","C0B"),("C1A","C1B")); S=A+tuple(x for p in C for x in p)
LOCAL=frozenset({("C0A","C0B"),("C1A","C1B")}); CANDS=tuple((a,b) for a in S for b in S if a!=b and (a,b) not in LOCAL)
sigs=collections.Counter();seen=set()
with open(SRC,newline="") as f:
 for r in csv.DictReader(f):
  if (r["D"],r["C"])!=("3","8"):continue
  seen.add((r["benchmark"],r["opt"]));n=int(r["occurrences"]);nodes=json.loads(r["signature"])
  keep=[i for i,(op,d) in enumerate(nodes) if not op.startswith("mul")];rem={x:i for i,x in enumerate(keep)}
  nn=[(nodes[x][0],[rem[d] for d in nodes[x][1] if d in rem]) for x in keep]
  if nn:sigs[json.dumps(nn,separators=(",",":"))]+=n
parsed={s:json.loads(s) for s in sigs}
def emb(nodes,links):
 if len(nodes)>8:return False
 ed=[(d,i) for i,(_,ds) in enumerate(nodes) for d in ds];order=sorted(range(len(nodes)),key=lambda u:-sum(u in e for e in ed));ass={};used=set()
 def rec(k):
  if k==len(nodes):return True
  u=order[k]
  for sl in S:
   if sl in used:continue
   if all(not(a==u and b in ass) or (sl,ass[b]) in links for a,b in ed) and all(not(b==u and a in ass) or (ass[a],sl) in links for a,b in ed):
    ass[u]=sl;used.add(sl)
    if rec(k+1):return True
    used.remove(sl);del ass[u]
  return False
 return rec(0)
score_cache={}
def score(extra):
 k=tuple(sorted(extra))
 if k not in score_cache:
  links=LOCAL|frozenset(extra);score_cache[k]=sum(w*len(parsed[s]) for s,w in sigs.items() if emb(parsed[s],links))
 return score_cache[k]
def cost(extra):
 ind=collections.Counter(b for a,b in extra);out=collections.Counter(a for a,b in extra)
 return (max(ind.values() or [0]),max(out.values() or [0]),sum(max(0,v-1) for v in ind.values()))
perms=[]
for ap in itertools.permutations(A):
 for cp in itertools.permutations((0,1)):
  m=dict(zip(A,ap))
  for old,new in enumerate(cp):m[f"C{old}A"]=f"C{new}A";m[f"C{old}B"]=f"C{new}B"
  perms.append(m)
def canon(extra):
 forms=[]
 for m in perms:forms.append(tuple(sorted((m[a],m[b]) for a,b in extra)))
 return min(forms)
beam={frozenset()}
levels={}
for k in range(1,max(KS)+1):
 cand={}
 for e0 in beam:
  for e in CANDS:
   if e in e0:continue
   x=frozenset(set(e0)|{e}); c=canon(x)
   if c in cand:continue
   cand[c]=x
 # keep score leaders while retaining low-cost alternatives
 ranked=sorted(cand.values(),key=lambda x:(score(x),-cost(x)[2],-cost(x)[0],-cost(x)[1]),reverse=True)
 beam=set(ranked[:BEAM]);levels[k]=list(beam)
 print("STEP4C2_LEVEL",k,"unique_candidates",len(cand),"beam",len(beam),"best_score",max(score(x) for x in beam))
print("STEP4C2_AUDIT pairs",len(seen),"signatures",len(sigs),"beam",BEAM,"permutations",len(perms))
with open("step4c2_pareto.csv","w",newline="") as f:
 w=csv.writer(f);w.writerow(["K","score","max_fanin","max_fanout","mux_proxy","canonical_links"])
 for k in KS:
  xs=levels[k]; pts=[]
  for x in xs:
   sc=score(x);ci,co,cm=cost(x)
   dominated=any(score(y)>=sc and all(a<=b for a,b in zip(cost(y),(ci,co,cm))) and (score(y)>sc or cost(y)!=(ci,co,cm)) for y in xs)
   if not dominated:pts.append(x)
  pts=sorted(pts,key=lambda x:(-score(x),cost(x),canon(x)))
  print("STEP4C2_PARETO",k,"count",len(pts))
  for rank,x in enumerate(pts[:20],1):
   ci,co,cm=cost(x); cc=canon(x)
   print("STEP4C2_CAND",k,rank,"score",score(x),"fanin",ci,"fanout",co,"mux",cm,"links",cc)
   w.writerow([k,score(x),ci,co,cm,json.dumps(cc)])
print("STEP4C2_LIMITATION beam search is constrained, not proof of global optimum; structural score excludes external operands/liveouts, routing, timing, area, cycles, IPC and speedup")
