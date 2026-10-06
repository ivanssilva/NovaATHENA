#!/usr/bin/env python3
import csv,collections,statistics
rows=list(csv.DictReader(open('step4d1_refined_counts.csv')))
A=collections.defaultdict(list)
for r in rows:
 A[(r['benchmark'],r['opt'])].append((int(r['ops']),int(r['true_liveins']),int(r['true_liveouts']),int(r['occurrences'])))
print('STEP4D2_AUDIT pairs',len(A),'rows',len(rows))
for opt in ('O2','O3'):
 keys=sorted(k for k in A if k[1]==opt)
 for ni,no in [(3,3),(4,3),(4,4),(5,4),(4,5),(5,5),(6,4),(5,6)]:
  gf=[];of=[]
  for k in keys:
   rr=A[k]; tg=sum(n for _,_,_,n in rr); to=sum(op*n for op,_,_,n in rr)
   g=sum(n for op,li,lo,n in rr if li<=ni and lo<=no)
   o=sum(op*n for op,li,lo,n in rr if li<=ni and lo<=no)
   gf.append(g/tg);of.append(o/to)
  print('STEP4D2_JOINT',opt,'in',ni,'out',no,
        'group_med',f'{statistics.median(gf):.9f}','group_q1',f'{statistics.quantiles(gf,n=4,method="inclusive")[0]:.9f}',
        'op_med',f'{statistics.median(of):.9f}','op_q1',f'{statistics.quantiles(of,n=4,method="inclusive")[0]:.9f}')
print('STEP4D2_NOTE group=joint fraction of G_t occurrences; op=joint fraction of operations inside G_t. Benchmark-balanced medians/Q1, not pooled fractions.')
