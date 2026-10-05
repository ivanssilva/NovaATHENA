#!/usr/bin/env python3
"""ATHENA Step 4B: topology-family structural mapping.
Uses exact D=3,C=8 G_t signatures. Structural experiment only: no cycle/speedup claim.
Compares progressively richer communication capabilities after local C2 packing.
"""
import csv,json,collections,statistics,itertools
SRC="gt_capacity_benchmark_signature_counts.csv"
# T0: local C2 only; T1: + directed producer->consumer inter-PE edges;
# T2: + selective two-producer convergence; T3: unrestricted internal DAG (upper bound).
TOPO=("T0_LOCAL_C2","T1_CHAIN_LINKS","T2_SELECTIVE_JOIN","T3_FULL_DAG")
tot=collections.Counter(); acc={t:collections.Counter() for t in TOPO}; seen=set()

def best_local_c2(nodes,K=2):
 cand=[]
 for b,(op,deps) in enumerate(nodes):
  if op.startswith("mul"): continue
  for a in deps:
   if not nodes[a][0].startswith("mul"): cand.append(frozenset((a,b)))
 best=(0,frozenset())
 def rec(pos,used,count):
  nonlocal best
  if len(used)>best[0]: best=(len(used),used)
  if count==K:return
  for z in range(pos,len(cand)):
   S=cand[z]
   if not S&used:rec(z+1,used|S,count+1)
 rec(0,frozenset(),0);return best[1]

def classify(nodes):
 edges=[(a,b) for b,(_,deps) in enumerate(nodes) for a in deps]
 indeg=collections.Counter(b for a,b in edges)
 # MUL edges are temporally separate and are not claimed as same-cycle topology coverage.
 nonmul=[(a,b) for a,b in edges if not nodes[a][0].startswith("mul") and not nodes[b][0].startswith("mul")]
 return edges,nonmul,indeg

with open(SRC,newline="") as f:
 for r in csv.DictReader(f):
  if (r["D"],r["C"])!=("3","8"):continue
  key=(r["benchmark"],r["opt"]);seen.add(key);n=int(r["occurrences"]);nodes=json.loads(r["signature"])
  edges,nonmul,indeg=classify(nodes); local=best_local_c2(nodes,2)
  local_edges=sum(1 for a,b in nonmul if a in local and b in local)
  chain_res=sum(1 for a,b in nonmul if indeg[b]<2 and not(a in local and b in local))
  join_res=sum(1 for a,b in nonmul if indeg[b]>=2 and not(a in local and b in local))
  vals={
   "operations":len(nodes),"nonmul_edges":len(nonmul),"local_c2_edges":local_edges,
   "residual_chain_edges":chain_res,"residual_join_edges":join_res,
   "mul_edges":len(edges)-len(nonmul)}
  for k,v in vals.items():tot[key,k]+=n*v
  # Edge realizability proxy under nested communication capability sets.
  caps={
   "T0_LOCAL_C2":local_edges,
   "T1_CHAIN_LINKS":local_edges+chain_res,
   "T2_SELECTIVE_JOIN":local_edges+chain_res+join_res,
   "T3_FULL_DAG":len(nonmul)}
  for t,v in caps.items():acc[t][key]+=n*v
assert len(seen)==38,len(seen)
with open("step4b_topology_mapping.csv","w",newline="") as f:
 w=csv.writer(f);w.writerow(["benchmark","opt","topology","realizable_nonmul_edges","nonmul_edges","edge_fraction"])
 for key in sorted(seen):
  for t in TOPO:
   den=tot[key,"nonmul_edges"];w.writerow([*key,t,acc[t][key],den,(acc[t][key]/den if den else 1.0)])
print("STEP4B_AUDIT benchmark_opt_pairs",len(seen),"D=3 C=8 K_C2=2")
for o in ("O2","O3"):
 keys=[k for k in seen if k[1]==o]
 print("STEP4B_EDGE_COUNTS",o,"nonmul",sum(tot[k,"nonmul_edges"] for k in keys),"local_c2",sum(tot[k,"local_c2_edges"] for k in keys),"residual_chain",sum(tot[k,"residual_chain_edges"] for k in keys),"residual_join",sum(tot[k,"residual_join_edges"] for k in keys),"mul_temporal",sum(tot[k,"mul_edges"] for k in keys))
 for t in TOPO:
  v=sorted((acc[t][k]/tot[k,"nonmul_edges"] if tot[k,"nonmul_edges"] else 1.0) for k in keys)
  print("STEP4B_TOPO",o,t,"median_edge_fraction",statistics.median(v),"q1",statistics.median(v[:len(v)//2]),"q3",statistics.median(v[(len(v)+1)//2:]))
print("STEP4B_LIMITATION edge realizability is structural capability, not placement, routing delay, cycles, IPC, or speedup")
