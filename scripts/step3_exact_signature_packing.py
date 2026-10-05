#!/usr/bin/env python3
"""Paired marginal and simultaneous multiplicity analysis for ATHENA Step 3."""
import csv,json,statistics,collections
D,C='3','8'
def q(v):
 v=sorted(v); n=len(v)
 return statistics.median(v),statistics.median(v[:n//2]),statistics.median(v[(n+1)//2:])
def candidates(nodes,ac,aj):
 out=[]
 if ac:
  for b,(op,deps) in enumerate(nodes):
   if op.startswith('mul'): continue
   for a in deps:
    if not nodes[a][0].startswith('mul'): out.append((frozenset((a,b)),'C2'))
 if aj:
  for z,(op,deps) in enumerate(nodes):
   if op.startswith('mul') or len(deps)<2: continue
   ds=[d for d in deps if not nodes[d][0].startswith('mul')]
   for i in range(len(ds)):
    for j in range(i+1,len(ds)): out.append((frozenset((ds[i],ds[j],z)),'J'))
 return out
def best(nodes,ac,aj):
 cand=candidates(nodes,ac,aj); best=(0,0,0)
 def rec(k,used,a,c2,j):
  nonlocal best
  if (a,c2+j,j)>(best[0],best[1]+best[2],best[2]): best=(a,c2,j)
  for z in range(k,len(cand)):
   S,t=cand[z]
   if not S&used: rec(z+1,used|S,a+len(S),c2+(t=='C2'),j+(t=='J'))
 rec(0,frozenset(),0,0,0); return best
rows=[r for r in csv.DictReader(open('gt_capacity_benchmark_signature_counts.csv')) if r['D']==D and r['C']==C]
tot=collections.Counter(); absorb={x:collections.Counter() for x in ('C2','J','C2+J')}
hist={x:collections.Counter() for x in ('C2','J','C2+J')}
for r in rows:
 k=(r['benchmark'],r['opt']); occ=int(r['occurrences']); nodes=json.loads(r['signature']); tot[k]+=occ*len(nodes)
 for lab,ac,aj in [('C2',1,0),('J',0,1),('C2+J',1,1)]:
  a,nc,nj=best(nodes,ac,aj); absorb[lab][k]+=occ*a
  count=nc if lab=='C2' else nj if lab=='J' else nc+nj
  hist[(lab if lab in hist else 'C2+J')][(r['opt'],count)]+=occ
assert len(tot)==38
marg=[]
for opt in ('O2','O3'):
 keys=[k for k in tot if k[1]==opt]
 for name,a,b in [('J|C2','C2+J','C2'),('C2|J','C2+J','J')]:
  v=[(absorb[a][k]-absorb[b][k])/tot[k] for k in keys]; med,q1,q3=q(v)
  marg.append([opt,name,med,q1,q3,sum(x>0 for x in v)])
with open('step3_paired_marginals.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['opt','marginal','median','q1','q3','benchmarks_positive']);w.writerows(marg)
mult=[]
for opt in ('O2','O3'):
 for lab in ('C2','J','C2+J'):
  den=sum(v for (o,n),v in hist[lab].items() if o==opt)
  mean=sum(n*v for (o,n),v in hist[lab].items() if o==opt)/den
  for n in sorted(n for (o,n) in hist[lab] if o==opt):
   v=hist[lab][(opt,n)]; mult.append([opt,lab,n,v,v/den,mean])
with open('step3_simultaneous_multiplicity.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['opt','motif_set','packed_motifs_per_Gt','Gt_occurrences','fraction_of_Gt','mean_packed_motifs']);w.writerows(mult)
print('STEP3_PAIRED_COMPLETE',len(tot))
for r in marg: print('STEP3_MARGINAL',*r)
for opt in ('O2','O3'):
 for lab in ('C2','J','C2+J'):
  den=sum(v for (o,n),v in hist[lab].items() if o==opt)
  mean=sum(n*v for (o,n),v in hist[lab].items() if o==opt)/den
  p2=sum(v for (o,n),v in hist[lab].items() if o==opt and n>=2)/den
  p3=sum(v for (o,n),v in hist[lab].items() if o==opt and n>=3)/den
  print('STEP3_MULT',opt,lab,'mean',mean,'P>=2',p2,'P>=3',p3)


# Finite C2 multiplicity: maximum absorbed operations with at most K non-overlapping C2 motifs.
def best_c2_k(nodes,K):
 cand=candidates(nodes,1,0); best_abs=0
 def rec(pos,used,count,absorb):
  nonlocal best_abs
  if absorb>best_abs: best_abs=absorb
  if count==K: return
  for z in range(pos,len(cand)):
   S,_=cand[z]
   if not S&used: rec(z+1,used|S,count+1,absorb+2)
 rec(0,frozenset(),0,0); return best_abs
c2k={K:collections.Counter() for K in (1,2,3,4)}
for r in rows:
 k=(r['benchmark'],r['opt']); occ=int(r['occurrences']); nodes=json.loads(r['signature'])
 for K in c2k: c2k[K][k]+=occ*best_c2_k(nodes,K)
with open('step3_c2_finite_multiplicity.csv','w',newline='') as f:
 w=csv.writer(f); w.writerow(['benchmark','opt','K','absorbed_ops','eligible_ops','absorbed_fraction'])
 for k in sorted(tot):
  for K in c2k: w.writerow([k[0],k[1],K,c2k[K][k],tot[k],c2k[K][k]/tot[k]])
summary=[]
for opt in ('O2','O3'):
 keys=[k for k in tot if k[1]==opt]
 for K in (1,2,3,4):
  v=[c2k[K][k]/tot[k] for k in keys]; med,q1,q3=q(v)
  summary.append([opt,K,med,q1,q3])
with open('step3_c2_finite_multiplicity_summary.csv','w',newline='') as f:
 w=csv.writer(f); w.writerow(['opt','K','median_absorbed_fraction','q1','q3']); w.writerows(summary)
for r in summary: print('STEP3_C2K',*r)


# Step 3A: paired benchmark-level marginal gain of each additional finite C2.
paired=[]
for opt in ('O2','O3'):
 keys=[k for k in tot if k[1]==opt]
 for k0,k1 in ((1,2),(2,3),(3,4)):
  v=[(c2k[k1][k]-c2k[k0][k])/tot[k] for k in keys]
  med,q1,q3=q(v)
  paired.append([opt,f'{k0}->{k1}',med,q1,q3,sum(x>0 for x in v),max(v)])
with open('step3_c2_paired_marginals.csv','w',newline='') as f:
 w=csv.writer(f); w.writerow(['opt','transition','median_marginal','q1','q3','benchmarks_positive','max_marginal']); w.writerows(paired)
for r in paired: print('STEP3_C2_PAIRED',*r)
