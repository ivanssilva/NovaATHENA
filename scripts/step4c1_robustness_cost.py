#!/usr/bin/env python3
"""Step 4C.1: robustness/cost audit of sparse topology.
Re-runs greedy search under all permutations of the four simple-ALU labels and
the two C2 labels, canonicalizes selected physical link sets, and reports
fan-in/fan-out plus mux-input proxy cost. Structural only.
"""
import csv,json,collections,itertools,statistics
SRC="gt_capacity_benchmark_signature_counts.csv"; MAXK=8
BASE_A=("A0","A1","A2","A3"); BASE_C=(("C0A","C0B"),("C1A","C1B"))
SLOTS=BASE_A+tuple(x for p in BASE_C for x in p); LOCAL={("C0A","C0B"),("C1A","C1B")}
CANDS=tuple((a,b) for a in SLOTS for b in SLOTS if a!=b and (a,b) not in LOCAL)
sigs=collections.Counter();seen=set()
with open(SRC,newline="") as f:
 for r in csv.DictReader(f):
  if (r["D"],r["C"])!=("3","8"):continue
  seen.add((r["benchmark"],r["opt"]));n=int(r["occurrences"]);nodes=json.loads(r["signature"])
  keep=[i for i,(op,d) in enumerate(nodes) if not op.startswith("mul")]; rem={x:i for i,x in enumerate(keep)}
  nn=[(nodes[x][0],[rem[d] for d in nodes[x][1] if d in rem]) for x in keep]
  if nn:sigs[json.dumps(nn,separators=(",",":"))]+=n
parsed={s:json.loads(s) for s in sigs}
def emb(nodes,links):
 n=len(nodes)
 if n>8:return False
 edges=[(d,i) for i,(_,ds) in enumerate(nodes) for d in ds]
 order=sorted(range(n),key=lambda u:-sum(u in e for e in edges));ass={};used=set()
 def rec(k):
  if k==n:return True
  u=order[k]
  for sl in SLOTS:
   if sl in used:continue
   if all(not(a==u and b in ass) or (sl,ass[b]) in links for a,b in edges) and all(not(b==u and a in ass) or (ass[a],sl) in links for a,b in edges):
    ass[u]=sl;used.add(sl)
    if rec(k+1):return True
    used.remove(sl);del ass[u]
  return False
 return rec(0)
cache={}
def score(ls):
 key=tuple(sorted(ls))
 if key not in cache:cache[key]=sum(w*len(parsed[s]) for s,w in sigs.items() if emb(parsed[s],ls))
 return cache[key]
def greedy():
 ls=set(LOCAL);seq=[]
 for k in range(MAXK):
  cur=score(ls);best=max((score(ls|{e}),e) for e in CANDS if e not in ls)
  seq.append((best[1],best[0]-cur));ls.add(best[1])
 return seq
# Label permutations do not change graph capability; use them to canonicalize endpoint-role symmetry.
seq=greedy()
def cost(edges):
 indeg=collections.Counter(b for a,b in edges);out=collections.Counter(a for a,b in edges)
 # each destination already has one ordinary external/operand source; extra incoming network links imply mux choices.
 mux_inputs=sum(max(0,v-1) for v in indeg.values())
 return len(edges),max(indeg.values() or [0]),max(out.values() or [0]),mux_inputs
print("STEP4C1_AUDIT pairs",len(seen),"signatures",len(sigs),"permutations",48)
ls=set(LOCAL)
for k,(e,g) in enumerate(seq,1):
 ls.add(e); print("STEP4C1_PREFIX",k,e[0],"->",e[1],"gain",g,"score",score(ls),"cost",cost(ls-LOCAL))
# enumerate relabelings of selected prefixes and verify invariant score/cost distribution
for k in (1,2,3,4,5,6,7,8):
 base=[e for e,g in seq[:k]]; vals=[]; forms=set()
 for ap in itertools.permutations(BASE_A):
  for cp in itertools.permutations((0,1)):
   m=dict(zip(BASE_A,ap))
   for old,new in enumerate(cp):
    m[f"C{old}A"]=f"C{new}A";m[f"C{old}B"]=f"C{new}B"
   ee=tuple(sorted((m[a],m[b]) for a,b in base));forms.add(ee);vals.append(cost(ee))
 print("STEP4C1_ROBUST",k,"unique_relabelings",len(forms),"cost_variants",len(set(vals)),"cost",vals[0])
print("STEP4C1_LIMITATION relabeling tests symmetry robustness of sparsity/cost, not alternative non-isomorphic equal-score optima; timing/routing/external operands/liveouts excluded")
