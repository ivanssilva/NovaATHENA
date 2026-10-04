#!/usr/bin/env python3
"""Exact-signature packing evidence for ATHENA Step 3.
Uses aggregated G_t signatures (D=3,C=8). It does NOT call the result speedup or
hardware coverage. PE-ALU is universal for one eligible op, so unconstrained
Cov(H) would be trivially 100%; instead we measure maximum non-overlapping
multi-op absorption by candidate composite PE motifs.
"""
import csv,json,statistics,collections
D,C='3','8'
def q(v):
 v=sorted(v);n=len(v);return statistics.median(v),statistics.median(v[:n//2]),statistics.median(v[(n+1)//2:])
def candidates(nodes,allow_c2,allow_j):
 n=len(nodes); out=[]
 if allow_c2:
  for b,(op,deps) in enumerate(nodes):
   if op.startswith('mul'): continue
   for a in deps:
    if not nodes[a][0].startswith('mul'): out.append((frozenset((a,b)),'C2'))
 if allow_j:
  for c,(op,deps) in enumerate(nodes):
   if op.startswith('mul') or len(deps)<2: continue
   ds=[d for d in deps if not nodes[d][0].startswith('mul')]
   for i in range(len(ds)):
    for j in range(i+1,len(ds)): out.append((frozenset((ds[i],ds[j],c)),'J'))
 return out
def best(nodes,ac,aj):
 cand=candidates(nodes,ac,aj); best=(0,0,0) # absorbed, c2, j
 def rec(k,used,absorb,c2,j):
  nonlocal best
  if (absorb,c2+j,j)> (best[0],best[1]+best[2],best[2]): best=(absorb,c2,j)
  for z in range(k,len(cand)):
   S,t=cand[z]
   if not (S&used): rec(z+1,used|S,absorb+len(S),c2+(t=='C2'),j+(t=='J'))
 rec(0,frozenset(),0,0,0);return best
rows=list(csv.DictReader(open('gt_capacity_benchmark_signature_counts.csv')))
rows=[r for r in rows if r['D']==D and r['C']==C]
assert rows
tot=collections.Counter(); vals={x:collections.Counter() for x in ('C2','J','C2+J')}
for r in rows:
 k=(r['benchmark'],r['opt']); occ=int(r['occurrences']); nodes=json.loads(r['signature']); tot[k]+=occ*len(nodes)
 for label,ac,aj in [('C2',1,0),('J',0,1),('C2+J',1,1)]:
  a,_,_=best(nodes,ac,aj);vals[label][k]+=occ*a
assert len(tot)==38
out=[]
for opt in ('O2','O3'):
 for label in ('C2','J','C2+J'):
  v=[vals[label][k]/tot[k] for k in tot if k[1]==opt]; med,q1,q3=q(v)
  out.append([opt,label,med,q1,q3,sum(x>0 for x in v)])
with open('step3_exact_signature_packing.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['opt','candidate_motifs','median_absorbed_op_fraction','q1','q3','benchmarks_nonzero']);w.writerows(out)
with open('step3_exact_signature_packing.md','w') as f:
 f.write('# Step 3 exact-signature motif packing\n\n')
 f.write('D=3,C=8. Exact graph signatures are parsed as (operation, internal predecessor IDs). ')
 f.write('Maximum non-overlapping packing is solved exhaustively per distinct signature and occurrence-weighted per benchmark.\n\n')
 f.write('Important methodological correction: because PE-ALU can realize any single eligible non-MUL ALU op, unconstrained Cov({PE-ALU}) is trivially 100% of that universe. Therefore this analysis does NOT report total PE coverage or speedup. It reports the fraction of eligible operations absorbable into non-overlapping multi-op C2/J motifs. Exact hardware coverage requires PE multiplicities, timing and topology constraints.\n\n')
 for r in out:f.write('%s %s median=%.6f IQR=[%.6f,%.6f] nonzero=%d/19\n'%tuple(r))
print('STEP3_EXACT_PACKING_COMPLETE',len(tot),'benchmark-opt pairs')
for r in out:print('STEP3_PACK',*r)
