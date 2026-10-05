#!/usr/bin/env python3
"""Step 4A: exact-signature internal communication census; no topology assumed."""
import csv,json,collections,statistics
SRC="gt_capacity_benchmark_signature_counts.csv"
agg=collections.Counter(); bench=collections.defaultdict(collections.Counter); seen=set()
with open(SRC,newline="") as f:
 for r in csv.DictReader(f):
  if (r["D"],r["C"])!=("3","8"): continue
  b,o=r["benchmark"],r["opt"]; seen.add((b,o)); n=int(r["occurrences"]); nodes=json.loads(r["signature"])
  indeg=[len(d) for _,d in nodes]; succ=collections.Counter(x for _,d in nodes for x in d); edges=sum(indeg)
  mul_edges=sum(1 for i,(_,deps) in enumerate(nodes) for d in deps if nodes[i][0].startswith("mul") or nodes[d][0].startswith("mul"))
  vals={"groups":1,"operations":len(nodes),"internal_edges":edges,"nonmul_internal_edges":edges-mul_edges,
        "edges_touching_mul":mul_edges,"join_nodes":sum(x>=2 for x in indeg),"fork_nodes":sum(x>=2 for x in succ.values()),
        "groups_with_join":int(any(x>=2 for x in indeg)),"groups_with_fork":int(any(x>=2 for x in succ.values())),
        "groups_with_mul_edge":int(mul_edges>0),"independent_nodes":sum(x==0 for x in indeg)}
  for k,v in vals.items(): bench[(b,o)][k]+=n*v; agg[o,k]+=n*v
assert len(seen)==38,len(seen)
fields=["benchmark","opt","groups","operations","internal_edges","nonmul_internal_edges","edges_touching_mul","join_nodes","fork_nodes","groups_with_join","groups_with_fork","groups_with_mul_edge","independent_nodes"]
with open("step4a_internal_communication.csv","w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for (b,o),v in sorted(bench.items()):w.writerow({"benchmark":b,"opt":o,**v})
print("STEP4A_AUDIT benchmark_opt_pairs",len(seen))
for o in ("O2","O3"):
 print("STEP4A_GLOBAL",o,json.dumps({k:agg[o,k] for k in fields[2:]},sort_keys=True))
 for k in ("internal_edges","nonmul_internal_edges","edges_touching_mul"):
  v=[bench[(b,o)][k]/bench[(b,o)]["operations"] for b,x in seen if x==o]
  print("STEP4A_BALANCED",o,k,"median_per_operation",statistics.median(v),"q1",statistics.median(sorted(v)[:len(v)//2]),"q3",statistics.median(sorted(v)[(len(v)+1)//2:]))
print("STEP4A_LIMITATION external operand identities and true future liveouts absent; counts are structural, not routing delay or performance")
