#!/usr/bin/env python3
import csv,json,collections,statistics,sys
p=sys.argv[1] if len(sys.argv)>1 else 'gt_capacity_benchmark_signature_counts.csv'
rows=[]
with open(p,newline='') as f:
 for r in csv.DictReader(f):
  if int(r['D'])==3 and int(r['C'])==8: rows.append(r)
tot=collections.Counter(); mul=collections.Counter(); gt_occ=collections.Counter(); gt_mul=collections.Counter(); mul_nodes_hist=collections.Counter()
roles=collections.Counter()
for r in rows:
 k=(r['benchmark'],r['opt']); occ=int(r['occurrences']); nodes=json.loads(r['signature']); n=len(nodes)
 tot[k]+=occ*n; gt_occ[k]+=occ
 mids=[i for i,(op,deps) in enumerate(nodes) if 'mul' in op.lower()]
 mul[k]+=occ*len(mids)
 if mids: gt_mul[k]+=occ
 mul_nodes_hist[(k,len(mids))]+=occ
 for i in mids:
  op,deps=nodes[i]; consumers=sum(1 for _,ds in nodes if i in ds)
  indeg=len(deps)
  role=('isolated' if indeg==0 and consumers==0 else
        'source' if indeg==0 and consumers>0 else
        'sink' if indeg>0 and consumers==0 else 'internal')
  roles[(k,role)]+=occ
def q(v):
 v=sorted(v); n=len(v)
 def pct(p):
  x=(n-1)*p; a=int(x); b=min(a+1,n-1); return v[a]*(b-x)+v[b]*(x-a)
 return statistics.median(v),pct(.25),pct(.75)
with open('step3b_mul_per_benchmark.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['benchmark','opt','eligible_ops','mul_ops','mul_fraction','gt_occurrences','gt_with_mul','gt_with_mul_fraction','mul_isolated','mul_source','mul_sink','mul_internal'])
 for k in sorted(tot):
  w.writerow([*k,tot[k],mul[k],mul[k]/tot[k],gt_occ[k],gt_mul[k],gt_mul[k]/gt_occ[k]]+[roles[(k,x)] for x in ('isolated','source','sink','internal')])
for opt in ('O2','O3'):
 keys=[k for k in tot if k[1]==opt]
 for metric,vals in [('mul_fraction',[mul[k]/tot[k] for k in keys]),('gt_with_mul_fraction',[gt_mul[k]/gt_occ[k] for k in keys])]:
  med,q1,q3=q(vals); print('STEP3B_MUL',opt,metric,med,q1,q3,sum(x>0 for x in vals))
 # occurrence-weighted multiplicity of MUL in G_t
 den=sum(gt_occ[k] for k in keys)
 for m in (1,2,3):
  num=sum(v for (k,c),v in mul_nodes_hist.items() if k in keys and c>=m)
  print('STEP3B_MUL_MULT',opt,'P_GT_MUL_GE',m,num/den)
print('STEP3B_MUL_COMPLETE',len({k for k in tot}))
