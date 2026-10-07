#!/usr/bin/env python3
"""Corrected Step 5B C2 optimistic temporal upper bound."""
import csv,glob,os,heapq,statistics
A={'zero':'x0','ra':'x1','sp':'x2','gp':'x3','tp':'x4','t0':'x5','t1':'x6','t2':'x7','s0':'x8','fp':'x8','s1':'x9','a0':'x10','a1':'x11','a2':'x12','a3':'x13','a4':'x14','a5':'x15','a6':'x16','a7':'x17','s2':'x18','s3':'x19','s4':'x20','s5':'x21','s6':'x22','s7':'x23','s8':'x24','s9':'x25','s10':'x26','s11':'x27','t3':'x28','t4':'x29','t5':'x30','t6':'x31'}
RR={'add','sub','and','or','xor','sll','srl','sra','slt','sltu'};RI={'addi','andi','ori','xori','slli','srli','srai','slti','sltiu'}
def n(x):return A.get(x.strip(),x.strip())
def elig(op,a):
 a=[n(x) for x in a]
 if op in RR and len(a)>=3:return a[0],[a[1],a[2]]
 if op in RI and len(a)>=2:return a[0],[a[1]]
def dag(nodes):
 p=[set() for _ in nodes];s=[[] for _ in nodes];last={}
 for i,(d,src) in enumerate(nodes):
  for r in src:
   if r!='x0' and r in last:p[i].add(last[r])
  if d!='x0':last[d]=i
 for i in range(len(nodes)):
  for u in p[i]:s[u].append(i)
 return p,s
def schedule(nodes,width,pairs=0):
 p,s=dag(nodes);done=set();cy=fusions=0
 while len(done)<len(nodes):
  ready=[i for i in range(len(nodes)) if i not in done and p[i]<=done]
  chosen=[];used=set();fc=0
  for u in ready:
   if len(chosen)>=width:break
   if u in used:continue
   chosen.append(u);used.add(u)
   if pairs and fc<pairs and len(chosen)<width:
    cand=[v for v in s[u] if v not in done and v not in used and (p[v]-done)=={u}]
    if cand:
     v=min(cand);chosen.append(v);used.add(v);fc+=1
  assert chosen and fc<=pairs
  done.update(chosen);cy+=1;fusions+=fc
 return cy,fusions
paths=sorted(glob.glob('embench-results/*_O*.trace.csv'));assert len(paths)==38
rows=[];tf=0
for path in paths:
 name=os.path.basename(path).replace('.trace.csv','');b,opt=name.rsplit('_',1);eps=[];cur=[]
 for r in csv.DictReader(open(path)):
  q=elig(r['op'].lower(),[x.strip() for x in r['args'].split(',') if x.strip()])
  if q:cur.append(q)
  elif cur:eps.append(cur);cur=[]
 if cur:eps.append(cur)
 h=w=c=f=0
 for e in eps:
  x,_=schedule(e,4);h+=x;x,_=schedule(e,8);w+=x;x,ff=schedule(e,8,2);c+=x;f+=ff
 assert c<=w<=h
 tf+=f;rows.append((b,opt,h,w,c,f,h/c,w/c))
 print('STEP5B_C2_TRACE',name,'h4',h,'w8',w,'c2',c,'fused',f,'h4_over_c2',f'{h/c:.9f}','w8_over_c2',f'{w/c:.9f}',flush=True)
with open('step5b_c2_corrected.csv','w',newline='') as z:
 q=csv.writer(z);q.writerow(['benchmark','opt','host4_cycles','generic8_cycles','c2_cycles','fused_pairs','h4_over_c2','w8_over_c2']);q.writerows(rows)
print('STEP5B_C2_AUDIT traces 38 pairs 38 invariant_c2_le_w8_le_h4 yes total_fusions',tf,flush=True)
assert tf>0
for opt in ('O2','O3'):
 z=[r for r in rows if r[1]==opt]
 for idx,label,numidx in [(6,'H4_OVER_C2',2),(7,'W8_OVER_C2',3)]:
  vals=[r[idx] for r in z];q=statistics.quantiles(vals,n=4)
  print('STEP5B_C2_RESULT',opt,label,'median',f'{statistics.median(vals):.9f}','q1',f'{q[0]:.9f}','q3',f'{q[2]:.9f}','aggregate',f'{sum(r[numidx] for r in z)/sum(r[4] for r in z):.9f}',flush=True)
print('STEP5B_C2_SCOPE corrected optimistic same-cycle C2 bound; max two producer-consumer fusions/cycle; eight positions; barriers unchanged.',flush=True)
print('STEP5B_C2_CAUTION cycle-count structural-temporal bound, not speedup; frequency penalty remains separate.',flush=True)
