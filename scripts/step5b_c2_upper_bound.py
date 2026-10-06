#!/usr/bin/env python3
"""Step 5B C2 optimistic temporal upper-bound experiment.

This deliberately measures the MAXIMUM cycle benefit available from up to two
same-cycle producer->consumer fusions per cycle, corresponding to two PE-C2s.
It is NOT an equal-clock performance claim. Timing is reported separately.

Same immutable eligible epochs and RAW graph as validated Step 5B. Barriers are
unchanged. A fused C2 pair consumes two of eight effective ALU positions and one
of two C2 pair opportunities. Consumer must have exactly one unsatisfied RAW
predecessor and all its other RAW predecessors must already be ready; producer
and consumer execute in the same cycle. Deterministic oldest-ready priority.
"""
import csv,glob,os,heapq,statistics
ALIASES={'zero':'x0','ra':'x1','sp':'x2','gp':'x3','tp':'x4','t0':'x5','t1':'x6','t2':'x7','s0':'x8','fp':'x8','s1':'x9','a0':'x10','a1':'x11','a2':'x12','a3':'x13','a4':'x14','a5':'x15','a6':'x16','a7':'x17','s2':'x18','s3':'x19','s4':'x20','s5':'x21','s6':'x22','s7':'x23','s8':'x24','s9':'x25','s10':'x26','s11':'x27','t3':'x28','t4':'x29','t5':'x30','t6':'x31'}
RR={'add','sub','and','or','xor','sll','srl','sra','slt','sltu'};RI={'addi','andi','ori','xori','slli','srli','srai','slti','sltiu'}
def n(x):return ALIASES.get(x.strip(),x.strip())
def elig(op,a):
 a=[n(x) for x in a]
 if op in RR and len(a)>=3:return a[0],[a[1],a[2]]
 if op in RI and len(a)>=2:return a[0],[a[1]]
 return None
def dag(nodes):
 N=len(nodes);pred=[set() for _ in range(N)];succ=[[] for _ in range(N)];last={}
 for i,(d,src) in enumerate(nodes):
  for s in src:
   if s!='x0' and s in last:pred[i].add(last[s])
  if d!='x0':last[d]=i
 for i in range(N):
  for p in pred[i]:succ[p].append(i)
 return pred,succ
def plain(nodes,w):
 pred,succ=dag(nodes);ind=[len(x) for x in pred];ready=[i for i,x in enumerate(ind) if x==0];heapq.heapify(ready);cy=done=0
 while done<len(nodes):
  now=[heapq.heappop(ready) for _ in range(min(w,len(ready)))];new=[]
  for u in now:
   done+=1
   for v in succ[u]:
    ind[v]-=1
    if ind[v]==0:new.append(v)
  for v in new:heapq.heappush(ready,v)
  cy+=1
 return cy
def c2(nodes):
 pred,succ=dag(nodes);ind=[len(x) for x in pred];ready=[i for i,x in enumerate(ind) if x==0];heapq.heapify(ready);cy=done=fused=0
 while done<len(nodes):
  slots=8;pairs=2;selected=[];selset=set()
  # oldest ready producers first; greedily fuse oldest eligible consumer
  while ready and slots>0:
   u=heapq.heappop(ready)
   if u in selset:continue
   selected.append(u);selset.add(u);slots-=1
   if pairs and slots:
    cand=[]
    for v in succ[u]:
     if v in selset:continue
     # all unsatisfied predecessors must be exactly {u}
     uns=[p for p in pred[v] if p not in completed and p not in selset]
     if uns==[u] or set(uns)=={u}:cand.append(v)
    if cand:
     v=min(cand);selected.append(v);selset.add(v);slots-=1;pairs-=1;fused+=1
  # ready items not selected remain for next cycle
  leftovers=[x for x in ready if x not in selset]
  completed.update(selected);done+=len(selected)
  # recompute readiness from completed to avoid same-cycle propagation beyond one edge
  ready=[]
  for v in range(len(nodes)):
   if v not in completed and all(p in completed for p in pred[v]):heapq.heappush(ready,v)
  for x in leftovers:
   if x not in completed and x not in ready:heapq.heappush(ready,x)
  cy+=1
 return cy,fused
paths=sorted(glob.glob('embench-results/*_O*.trace.csv'));assert len(paths)==38
rows=[]
for p in paths:
 global completed
 name=os.path.basename(p).replace('.trace.csv','');b,opt=name.rsplit('_',1);eps=[];cur=[]
 for r in csv.DictReader(open(p)):
  q=elig(r['op'].lower(),[x.strip() for x in r['args'].split(',') if x.strip()])
  if q:cur.append(q)
  else:
   if cur:eps.append(cur);cur=[]
 if cur:eps.append(cur)
 h=w=a=f=0
 for e in eps:
  h+=plain(e,4);w+=plain(e,8);completed=set();cc,ff=c2(e);a+=cc;f+=ff
 assert a<=w<=h
 rows.append((b,opt,h,w,a,f,h/a,w/a))
 print('STEP5B_C2_TRACE',name,'h4',h,'w8',w,'c2',a,'fused',f,'h4_over_c2',f'{h/a:.9f}','w8_over_c2',f'{w/a:.9f}',flush=True)
with open('step5b_c2_upper_bound.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['benchmark','opt','host4_cycles','generic8_cycles','c2_cycles','fused_pairs','h4_over_c2','w8_over_c2']);w.writerows(rows)
print('STEP5B_C2_AUDIT traces 38 pairs 38 invariant_c2_le_w8_le_h4 yes',flush=True)
for opt in ('O2','O3'):
 z=[r for r in rows if r[1]==opt]
 for idx,label in [(6,'H4_OVER_C2'),(7,'W8_OVER_C2')]:
  vals=[r[idx] for r in z];q=statistics.quantiles(vals,n=4)
  print('STEP5B_C2_RESULT',opt,label,'median',f'{statistics.median(vals):.9f}','q1',f'{q[0]:.9f}','q3',f'{q[2]:.9f}','aggregate',f'{sum(r[2 if idx==6 else 3] for r in z)/sum(r[4] for r in z):.9f}',flush=True)
print('STEP5B_C2_SCOPE optimistic same-cycle C2 cycle-count upper bound; two C2 fusions/cycle; eight effective positions; barriers unchanged; no MUL/memory/control/config timing.',flush=True)
print('STEP5B_C2_CAUTION not equal-clock speedup. Must be combined with measured/sensitivity clock period; current evidence gives PE-C2/ALU delay ratio 1.484802.',flush=True)
