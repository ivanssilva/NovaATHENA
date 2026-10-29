#!/usr/bin/env python3
"""E6 closed: symbolic break-even sensitivity from frozen E5 counts.
For attempt-level hit probability p=causal_reuse_hits/windows, a proxy gain
G=p*B-H-(1-p)*M requires B > H/p + ((1-p)/p)*M.
B,H,M are unknown cycles; this script NEVER invents cycle latencies or speedup.
"""
import csv,json,collections,hashlib,math
from pathlib import Path
src=Path('e5-input/e5_per_trace.csv')
assert src.exists(),'Missing frozen E5 artifact e5_per_trace.csv'
rows=list(csv.DictReader(src.open(newline='')))
assert len(rows)==114
out=[];agg=collections.defaultdict(lambda:collections.Counter())
for r in rows:
 k=int(r['group_BBs']);opt=r['opt'];w=int(r['windows']);h=int(r['causal_reuse_hits'])
 assert k in (2,4,8) and opt in ('O2','O3') and 0<=h<=w
 p=h/w if w else 0
 a=w/h if h else None
 b=(w-h)/h if h else None
 out.append(dict(benchmark=r['benchmark'],opt=opt,group_BBs=k,windows=w,causal_hits=h,p=round(p,12),H_coefficient=round(a,12) if a is not None else 'undefined',M_coefficient=round(b,12) if b is not None else 'undefined',zero_hits=int(h==0)))
 agg[(opt,k)].update(windows=w,hits=h)
assert len({(r['benchmark'],r['opt'],r['group_BBs']) for r in rows})==114
Path('e6-results').mkdir(exist_ok=True)
with open('e6-results/e6_per_trace.csv','w',newline='') as f:
 wr=csv.DictWriter(f,fieldnames=list(out[0]));wr.writeheader();wr.writerows(out)
with open('e6-results/e6_aggregate.csv','w',newline='') as f:
 fields=['opt','group_BBs','windows','causal_hits','p','H_coefficient','M_coefficient']
 wr=csv.DictWriter(f,fieldnames=fields);wr.writeheader()
 for opt in ('O2','O3'):
  for k in (2,4,8):
   c=agg[(opt,k)];w=c['windows'];h=c['hits']
   assert w>0 and h>0
   wr.writerow(dict(opt=opt,group_BBs=k,windows=w,causal_hits=h,p=round(h/w,12),H_coefficient=round(w/h,12),M_coefficient=round((w-h)/h,12)))
assert all(c['windows']>0 for c in agg.values()) and len(agg)==6
manifest=dict(experiment='E6-closed-symbolic-timing-sensitivity',source_e5_run=40913386156,source_e5_artifact='novaathena-e5-closed',source_e5_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),traces=38,rows=114,formula='G = p*B - H - (1-p)*M; break-even B > H/p + ((1-p)/p)*M for p>0',definitions=dict(p='causal reuse hits divided by all completed windows',B='unknown net benefit cycles conditional on correct reusable prediction',H='unknown overhead cycles charged on each window',M='unknown incremental penalty cycles per unsuccessful window'),limitations=['Sensitivity only: no assumed numerical hardware costs','The p value is a path-key reuse proxy, not CGRA config-cache hit rate','No mapping across control or memory, no correctness proof, no actual preparation timing','B,H,M must be supplied from independent microarchitectural measurements for numerical gain','No speedup computed; positive G is not a validated acceleration claim','The linear model is a first-order accounting identity, not a cycle-accurate simulator'])
Path('e6-results/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
Path('e6-results/README.md').write_text('# E6 closed — symbolic timing sensitivity\n\nUsing frozen E5 counts, p=causal_hits/windows. For an attempt-level expected gain proxy G=p B-H-(1-p) M, break-even is B>H/p+((1-p)/p)M. Report coefficients only; **no numerical latencies, speedup or actual CGRA configurations**. A zero-hit trace has undefined coefficients (no finite break-even with positive overhead). The model is explicitly conditional on unknown hardware timing.\n')
for opt in ('O2','O3'):
 for k in (2,4,8):
  c=agg[(opt,k)];print('E6_AGG',opt,k,'windows',c['windows'],'hits',c['hits'],'Hcoef',f"{c['windows']/c['hits']:.8f}",'Mcoef',f"{(c['windows']-c['hits'])/c['hits']:.8f}",flush=True)
print('E6_AUDIT_PASS traces 38 rows 114 aggregates 6',flush=True)
