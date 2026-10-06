#!/usr/bin/env python3
"""ATHENA Step 5B: explicit, reproducible idealized compute-only scheduler.

Scientific scope
----------------
This is a TRACE-DRIVEN MODEL, not measured hardware timing. It compares:
  H4: idealized 4-wide host scheduler;
  A8: idealized ATHENA structural scheduler.
Both consume the same dynamic architectural trace and the same true RAW graph.
The model intentionally removes memory stalls, branch misprediction and
configuration overhead. WAW/WAR are not dependencies because the comparison
assumes ideal renaming. Program-order barriers delimit scheduling epochs so
operations are never moved across control, memory, DIV/REM, or unsupported
instructions in this compute-only bound.

H4 issues at most four eligible integer compute operations per cycle.
A8 has eight effective ALU positions (4 PE-ALU + 2 PE-C2 stages) and the
validated K5 sparse links. For scientific conservatism in this first temporal
bound, dependent operations are NOT collapsed combinationally into the same
cycle: every RAW edge has minimum distance one cycle. Thus PE-C2 same-cycle
chaining is not assumed before a target-period timing contract is established.
MUL is deliberately a barrier in the primary 5B result because its L=6--8
temporal sensitivity belongs to Step 5C. This prevents silently treating MUL
as a one-cycle ALU.

Output is cycles for eligible non-MUL compute epochs only and their ratio.
It is NOT whole-application speedup.
"""
import csv,glob,os,re,heapq,collections,statistics,json
ALIASES={'zero':'x0','ra':'x1','sp':'x2','gp':'x3','tp':'x4','t0':'x5','t1':'x6','t2':'x7','s0':'x8','fp':'x8','s1':'x9','a0':'x10','a1':'x11','a2':'x12','a3':'x13','a4':'x14','a5':'x15','a6':'x16','a7':'x17','s2':'x18','s3':'x19','s4':'x20','s5':'x21','s6':'x22','s7':'x23','s8':'x24','s9':'x25','s10':'x26','s11':'x27','t3':'x28','t4':'x29','t5':'x30','t6':'x31'}
RR={'add','sub','and','or','xor','sll','srl','sra','slt','sltu'}
RI={'addi','andi','ori','xori','slli','srli','srai','slti','sltiu'}
MUL={'mul','mulh','mulhu','mulhsu'}
REG=re.compile(r'^(?:x(?:[12]?\\d|3[01])|zero|ra|sp|gp|tp|t[0-6]|s(?:[0-9]|1[01])|fp|a[0-7])$')
def n(x): return ALIASES.get(x.strip(),x.strip())
def elig(op,a):
 a=[n(x) for x in a]
 if op in RR and len(a)>=3:return a[0],[a[1],a[2]]
 if op in RI and len(a)>=2:return a[0],[a[1]]
 return None

def schedule_epoch(nodes,width):
 # nodes: (dst,srcs,global_seq). Build true RAW from last writer in epoch.
 N=len(nodes);pred=[set() for _ in range(N)];succ=[[] for _ in range(N)];last={}
 for i,(d,src,seq) in enumerate(nodes):
  for s in src:
   if s!='x0' and s in last:pred[i].add(last[s])
  if d!='x0':last[d]=i
 for i in range(N):
  for p in pred[i]:succ[p].append(i)
 indeg=[len(x) for x in pred];ready=[i for i,x in enumerate(indeg) if x==0]
 # deterministic oldest-dynamic-instruction priority.
 heapq.heapify(ready);cycles=0;issued=0
 while issued<N:
  if not ready:raise RuntimeError('RAW graph unexpectedly cyclic')
  this=[heapq.heappop(ready) for _ in range(min(width,len(ready)))]
  # successors become eligible next cycle, never same cycle.
  new=[]
  for u in this:
   issued+=1
   for v in succ[u]:
    indeg[v]-=1
    if indeg[v]==0:new.append(v)
  for v in new:heapq.heappush(ready,v)
  cycles+=1
 return cycles

paths=sorted(glob.glob('embench-results/*_O*.trace.csv'));assert len(paths)==38
out=[];total=collections.Counter()
for p in paths:
 name=os.path.basename(p).replace('.trace.csv','');b,opt=name.rsplit('_',1)
 epochs=[];cur=[];eligible=mulbar=bar=0
 for r in csv.DictReader(open(p)):
  op=r['op'].lower();a=[x.strip() for x in r['args'].split(',') if x.strip()]
  q=elig(op,a)
  if q:
   d,s=q;cur.append((d,s,int(r['seq'])));eligible+=1
  else:
   if cur:epochs.append(cur);cur=[]
   if op in MUL:mulbar+=1
   bar+=1
 if cur:epochs.append(cur)
 h=sum(schedule_epoch(e,4) for e in epochs);a8=sum(schedule_epoch(e,8) for e in epochs)
 ratio=(h/a8 if a8 else 1.0)
 out.append((b,opt,eligible,len(epochs),h,a8,ratio,mulbar,bar))
 total['eligible']+=eligible;total['epochs']+=len(epochs);total['h']+=h;total['a8']+=a8;total['mulbar']+=mulbar
 print('STEP5B_TRACE',name,'eligible',eligible,'epochs',len(epochs),'host4_cycles',h,'athena8_cycles',a8,'cycle_ratio',f'{ratio:.9f}',flush=True)
with open('step5b_temporal_results.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['benchmark','opt','eligible_nonmul_compute_ops','epochs','host4_cycles','athena8_cycles','equal_clock_cycle_ratio','mul_barriers','all_barriers']);w.writerows(out)
print('STEP5B_AUDIT traces',len(paths),'pairs',len(out),'eligible',total['eligible'],'epochs',total['epochs'],'host4_cycles',total['h'],'athena8_cycles',total['a8'],'mul_barriers',total['mulbar'],flush=True)
for opt in ('O2','O3'):
 z=[r for r in out if r[1]==opt];rat=[r[6] for r in z]
 # report median and quartiles; aggregate cycle ratio is also reported, not disguised as geometric mean.
 q=statistics.quantiles(rat,n=4)
 print('STEP5B_RESULT',opt,'benchmarks',len(z),'cycle_ratio_median',f'{statistics.median(rat):.9f}','q1',f'{q[0]:.9f}','q3',f'{q[2]:.9f}','aggregate_cycle_ratio',f'{sum(r[4] for r in z)/sum(r[5] for r in z):.9f}',flush=True)
print('STEP5B_SCOPE eligible_nonmul_integer_compute_epochs_only; equal clock; zero memory stalls; perfect control; zero configuration overhead; MUL and DIV/REM temporal effects excluded.',flush=True)
print('STEP5B_PRIORITY deterministic oldest-ready; ideal renaming means RAW only; barriers prevent cross-control/memory/divrem/unsupported motion.',flush=True)
print('STEP5B_CAUTION cycle_ratio is an idealized compute-only temporal bound for the explicitly modeled subset, NOT whole-application speedup and NOT measured OoO hardware performance.',flush=True)
