#!/usr/bin/env python3
"""ATHENA Step 4C: concrete slot/link search from exact G_t signatures.
Structural mapping only; no timing, cycles, IPC or speedup.
Slots: 4 simple ALU slots + 2 C2 slots (A/B internal link). Search added directed
inter-slot links greedily by weighted exact-signature embeddability. MUL excluded
from same-cycle mapping and remains a separate pipelined resource.
"""
import csv,json,collections,itertools,statistics
SRC="gt_capacity_benchmark_signature_counts.csv"
SLOTS=("A0","A1","A2","A3","C0A","C0B","C1A","C1B")
LOCAL={("C0A","C0B"),("C1A","C1B")}
CANDS=tuple((a,b) for a in SLOTS for b in SLOTS if a!=b and (a,b) not in LOCAL)
MAXLINKS=16
sigs=collections.Counter(); bybench=collections.defaultdict(collections.Counter); seen=set()
with open(SRC,newline="") as f:
 for r in csv.DictReader(f):
  if (r["D"],r["C"])!=("3","8"):continue
  key=(r["benchmark"],r["opt"]);seen.add(key); n=int(r["occurrences"]); nodes=json.loads(r["signature"])
  # non-MUL induced graph; MUL is temporal/separate
  keep=[i for i,(op,d) in enumerate(nodes) if not op.startswith("mul")]
  rem={old:i for i,old in enumerate(keep)}
  nn=[(nodes[old][0],[rem[d] for d in nodes[old][1] if d in rem]) for old in keep]
  if not nn:continue
  sig=json.dumps(nn,separators=(",",":"));sigs[sig]+=n;bybench[key][sig]+=n
assert len(seen)==38,len(seen)

def embeddable(nodes,links):
 n=len(nodes)
 if n>len(SLOTS):return False
 edges=[(d,i) for i,(_,ds) in enumerate(nodes) for d in ds]
 # degree/order heuristic
 order=sorted(range(n),key=lambda i:-(sum(1 for a,b in edges if a==i or b==i)))
 assign={};used=set()
 def rec(k):
  if k==n:return True
  u=order[k]
  for s in SLOTS:
   if s in used:continue
   ok=True
   for a,b in edges:
    if a==u and b in assign and (s,assign[b]) not in links:ok=False;break
    if b==u and a in assign and (assign[a],s) not in links:ok=False;break
   if ok:
    assign[u]=s;used.add(s)
    if rec(k+1):return True
    used.remove(s);del assign[u]
  return False
 return rec(0)

parsed={s:json.loads(s) for s in sigs}
cache={}
def covered(linkset,s):
 key=(tuple(sorted(linkset)),s)
 if key not in cache:cache[key]=embeddable(parsed[s],linkset)
 return cache[key]

links=set(LOCAL); chosen=[]
def score(ls):
 return sum(w*len(parsed[s]) for s,w in sigs.items() if covered(ls,s))
base=score(links); print("STEP4C_AUDIT benchmark_opt_pairs",len(seen),"signatures",len(sigs),"slots",len(SLOTS),"local_links",len(LOCAL))
print("STEP4C_BASE weighted_mapped_ops",base)
for k in range(1,MAXLINKS+1):
 best=None
 for e in CANDS:
  if e in links:continue
  sc=score(links|{e})
  cand=(sc,e)
  if best is None or cand>best:best=cand
 gain=best[0]-score(links);links.add(best[1]);chosen.append(best[1])
 print("STEP4C_LINK",k,best[1][0],"->",best[1][1],"gain_weighted_ops",gain,"total_weighted_ops",best[0])
 if gain==0:break

# benchmark-balanced mapped operation-weight proxy for each prefix
rows=[]
for key in sorted(seen):
 den=sum(w*len(parsed[s]) for s,w in bybench[key].items())
 ls=set(LOCAL)
 vals=[sum(w*len(parsed[s]) for s,w in bybench[key].items() if covered(ls,s))/den if den else 1.0]
 for e in chosen:
  ls.add(e);vals.append(sum(w*len(parsed[s]) for s,w in bybench[key].items() if covered(ls,s))/den if den else 1.0)
 for k,v in enumerate(vals):rows.append((*key,k,v))
with open("step4c_link_search.csv","w",newline="") as f:
 w=csv.writer(f);w.writerow(["benchmark","opt","added_links","mapped_operation_weight_fraction"]);w.writerows(rows)
for o in ("O2","O3"):
 for k in range(len(chosen)+1):
  v=sorted(r[3] for r in rows if r[1]==o and r[2]==k)
  print("STEP4C_BALANCED",o,"added_links",k,"median",statistics.median(v),"q1",statistics.median(v[:len(v)//2]),"q3",statistics.median(v[(len(v)+1)//2:]))
print("STEP4C_LIMITATION greedy link search and structural embeddability; slot count is a candidate capacity, not final physical topology; external operands/liveouts and routing/timing excluded")
