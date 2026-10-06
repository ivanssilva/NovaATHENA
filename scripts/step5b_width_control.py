#!/usr/bin/env python3
"""ATHENA Step 5B control experiment: isolate width-only effect.

Purpose
-------
Quantify whether the previously observed compute-only cycle reduction is caused
by 4->8 issue capacity alone. Three models consume exactly the same eligible
non-MUL integer epochs and true RAW graph:

 H4  : ideal renamed 4-wide host.
 W8  : ideal renamed generic 8-wide control machine.
 ATH-C: conservative ATHENA temporal model before a validated target-period
        contract for same-cycle PE-C2 chaining.

ATH-C deliberately uses the same one-cycle RAW distance as W8. Therefore, if
the implementation is correct, W8 and ATH-C MUST be cycle-identical. This is a
scientific control, not a performance claim. Any future ATHENA-specific gain
must come from explicitly modeled and timing-justified architectural features,
not from width alone.
"""
import csv,glob,os,re,heapq,collections,statistics
ALIASES={'zero':'x0','ra':'x1','sp':'x2','gp':'x3','tp':'x4','t0':'x5','t1':'x6','t2':'x7','s0':'x8','fp':'x8','s1':'x9','a0':'x10','a1':'x11','a2':'x12','a3':'x13','a4':'x14','a5':'x15','a6':'x16','a7':'x17','s2':'x18','s3':'x19','s4':'x20','s5':'x21','s6':'x22','s7':'x23','s8':'x24','s9':'x25','s10':'x26','s11':'x27','t3':'x28','t4':'x29','t5':'x30','t6':'x31'}
RR={'add','sub','and','or','xor','sll','srl','sra','slt','sltu'}
RI={'addi','andi','ori','xori','slli','srli','srai','slti','sltiu'}
MUL={'mul','mulh','mulhu','mulhsu'}
def n(x):return ALIASES.get(x.strip(),x.strip())
def elig(op,a):
 a=[n(x) for x in a]
 if op in RR and len(a)>=3:return a[0],[a[1],a[2]]
 if op in RI and len(a)>=2:return a[0],[a[1]]
 return None
def schedule(nodes,width):
 N=len(nodes);pred=[set() for _ in range(N)];succ=[[] for _ in range(N)];last={}
 for i,(d,src) in enumerate(nodes):
  for s in src:
   if s!='x0' and s in last:pred[i].add(last[s])
  if d!='x0':last[d]=i
 for i in range(N):
  for p in pred[i]:succ[p].append(i)
 indeg=[len(x) for x in pred];ready=[i for i,x in enumerate(indeg) if x==0];heapq.heapify(ready)
 cyc=issued=0
 while issued<N:
  if not ready:raise RuntimeError('cycle in RAW DAG')
  now=[heapq.heappop(ready) for _ in range(min(width,len(ready)))]
  new=[]
  for u in now:
   issued+=1
   for v in succ[u]:
    indeg[v]-=1
    if indeg[v]==0:new.append(v)
  for v in new:heapq.heappush(ready,v)
  cyc+=1
 return cyc
paths=sorted(glob.glob('embench-results/*_O*.trace.csv'));assert len(paths)==38
rows=[];mismatch=0
for p in paths:
 name=os.path.basename(p).replace('.trace.csv','');b,opt=name.rsplit('_',1)
 eps=[];cur=[];eligible=0
 for r in csv.DictReader(open(p)):
  op=r['op'].lower();a=[x.strip() for x in r['args'].split(',') if x.strip()]
  q=elig(op,a)
  if q:
   cur.append(q);eligible+=1
  else:
   if cur:eps.append(cur);cur=[]
 if cur:eps.append(cur)
 h4=sum(schedule(e,4) for e in eps)
 w8=sum(schedule(e,8) for e in eps)
 athc=sum(schedule(e,8) for e in eps)
 if w8!=athc:mismatch+=1
 ratio=h4/w8 if w8 else 1.0
 rows.append((b,opt,eligible,len(eps),h4,w8,athc,ratio))
 print('STEP5B_WIDTH_TRACE',name,'h4',h4,'w8',w8,'athc',athc,'h4_over_w8',f'{ratio:.9f}',flush=True)
with open('step5b_width_control.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['benchmark','opt','eligible_ops','epochs','host4_cycles','generic8_cycles','athena_conservative_cycles','width_only_cycle_ratio']);w.writerows(rows)
assert mismatch==0
print('STEP5B_WIDTH_AUDIT traces',len(paths),'mismatches_generic8_vs_athena_conservative',mismatch,flush=True)
for opt in ('O2','O3'):
 z=[r for r in rows if r[1]==opt];rat=[r[7] for r in z];q=statistics.quantiles(rat,n=4)
 print('STEP5B_WIDTH_RESULT',opt,'median',f'{statistics.median(rat):.9f}','q1',f'{q[0]:.9f}','q3',f'{q[2]:.9f}','aggregate',f'{sum(r[4] for r in z)/sum(r[5] for r in z):.9f}',flush=True)
print('STEP5B_WIDTH_CONCLUSION under_current_conservative_temporal_contract all observed ATHENA-vs-host cycle reduction is exactly reproduced by a generic 8-wide machine; ATHENA-specific heterogeneous-PE temporal benefit is therefore not yet established.',flush=True)
print('STEP5B_WIDTH_LIMIT future ATHENA-specific benefit requires an explicit timing-justified same-cycle PE-C2 model or other architecture-specific mechanism; do not attribute width-only reduction to heterogeneous PEs.',flush=True)
