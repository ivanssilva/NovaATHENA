#!/usr/bin/env python3
"""Step 5C: progressively realistic temporal model, first executable contract.
Keeps Step 5B C2 as frozen baseline; adds MUL L=6/7/8 (II=1) and audits
control/memory inputs needed by subsequent cumulative layers. No arbitrary
cache, predictor, configuration, or frequency parameters are invented.
"""
import csv,glob,os,statistics,collections
A={'zero':'x0','ra':'x1','sp':'x2','gp':'x3','tp':'x4','t0':'x5','t1':'x6','t2':'x7','s0':'x8','fp':'x8','s1':'x9','a0':'x10','a1':'x11','a2':'x12','a3':'x13','a4':'x14','a5':'x15','a6':'x16','a7':'x17','s2':'x18','s3':'x19','s4':'x20','s5':'x21','s6':'x22','s7':'x23','s8':'x24','s9':'x25','s10':'x26','s11':'x27','t3':'x28','t4':'x29','t5':'x30','t6':'x31'}
RR={'add','sub','and','or','xor','sll','srl','sra','slt','sltu'}; RI={'addi','andi','ori','xori','slli','srli','srai','slti','sltiu'}; MUL={'mul','mulh','mulhu','mulhsu'}
BR={'beq','bne','blt','bge','bltu','bgeu'}; JMP={'jal','jalr'}; MEM={'lb','lh','lw','lbu','lhu','sb','sh','sw'}
def n(x):return A.get(x.strip(),x.strip())
def dec(op,args):
 a=[n(x) for x in args]
 if op in RR|MUL and len(a)>=3:return a[0],[a[1],a[2]],op in MUL
 if op in RI and len(a)>=2:return a[0],[a[1]],False
 return None
def sched(nodes,width,pairs,mullat):
 # nodes=(dst,src,is_mul); true RAW only, ideal rename. MUL is pipelined II=1.
 N=len(nodes);pred=[set() for _ in nodes];succ=[[] for _ in nodes];last={}
 for i,(d,src,im) in enumerate(nodes):
  for r in src:
   if r!='x0' and r in last:pred[i].add(last[r])
  if d!='x0':last[d]=i
 for i in range(N):
  for u in pred[i]:succ[u].append(i)
 done={}; issued=set(); cyc=0; fus=0
 while len(issued)<N:
  ready=[i for i in range(N) if i not in issued and all(done.get(p,10**18)<=cyc for p in pred[i])]
  chosen=[]; used=set(); fc=0; mul_started=False
  for u in ready:
   if len(chosen)>=width:break
   if u in used:continue
   # one shared pipelined MUL, II=1 => at most one MUL starts per cycle
   if nodes[u][2] and mul_started:continue
   chosen.append(u);used.add(u)
   if nodes[u][2]:mul_started=True
   # C2 only for one-cycle ALU producer/consumer, never MUL
   if pairs and fc<pairs and not nodes[u][2] and len(chosen)<width:
    cand=[v for v in succ[u] if v not in issued and v not in used and not nodes[v][2] and (pred[v]-set(done))=={u}]
    if cand:
     v=min(cand);chosen.append(v);used.add(v);fc+=1
  if not chosen:
   cyc=min(done[p] for v in range(N) if v not in issued for p in pred[v] if p in done and done[p]>cyc);continue
  for u in chosen:
   issued.add(u);done[u]=cyc+(mullat if nodes[u][2] else (0 if u in used and any(u==v for x in chosen for v in []) else 1))
  # fused consumer completes with producer in this optimistic C2 bound
  if fc:
   # identify selected consumers whose only newly-unmet predecessor is selected producer
   for u in chosen:
    if not nodes[u][2]:
     for v in succ[u]:
      if v in chosen and (pred[v]-set(k for k,t in done.items() if t<=cyc))=={u}: done[v]=cyc+1
  fus+=fc;cyc+=1
 return (max(done.values()) if done else 0),fus
struct=sorted(glob.glob('structural/*_O*.trace.csv')+glob.glob('structural/**/*.trace.csv',recursive=True))
# de-duplicate recursive overlap
struct=sorted(set(struct)); assert len(struct)==38,len(struct)
mem=sorted(glob.glob('memory/**/*.memory.csv',recursive=True)); assert len(mem)==38,len(mem)
mmap={os.path.basename(p).replace('.memory.csv',''):p for p in mem}
rows=[]; audits=collections.Counter()
for p in struct:
 name=os.path.basename(p).replace('.trace.csv',''); b,opt=name.rsplit('_',1)
 rr=list(csv.DictReader(open(p))); epochs=[];cur=[];branches=jumps=memops=muls=0
 for r in rr:
  op=r['op'].lower(); args=[x.strip() for x in r['args'].split(',') if x.strip()]
  q=dec(op,args)
  if q: cur.append(q); muls+=int(q[2])
  else:
   if cur:epochs.append(cur);cur=[]
   branches+=op in BR; jumps+=op in JMP; memops+=op in MEM
 if cur:epochs.append(cur)
 mr=list(csv.DictReader(open(mmap[name]))); assert len(mr) in (memops,memops-1)
 audits.update(traces=1,branches=branches,jumps=jumps,memops=memops,captured_mem=len(mr),muls=muls)
 vals={}
 for L in (6,7,8):
  h=c=f=0
  for e in epochs:
   x,_=sched(e,4,0,L);h+=x
   x,ff=sched(e,8,2,L);c+=x;f+=ff
  vals[L]=(h,c,f)
 rows.append((b,opt,muls,branches,jumps,memops,len(mr),*[x for L in (6,7,8) for x in vals[L]]))
 print('STEP5C_TRACE',name,'mul',muls,'branch',branches,'jump',jumps,'mem',memops,'captured_mem',len(mr),
       *[f'L{L}_H4 {vals[L][0]} L{L}_C2 {vals[L][1]} L{L}_ratio {vals[L][0]/vals[L][1]:.9f}' for L in (6,7,8)],flush=True)
with open('step5c_progressive.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['benchmark','opt','mul_ops','branches','jumps','memory_ops','captured_memory','L6_H4','L6_C2','L6_fusions','L7_H4','L7_C2','L7_fusions','L8_H4','L8_C2','L8_fusions']);w.writerows(rows)
print('STEP5C_AUDIT',dict(audits),flush=True)
for opt in ('O2','O3'):
 z=[r for r in rows if r[1]==opt]
 for L,hi,ci in [(6,7,8),(7,10,11),(8,13,14)]:
  rat=[r[hi]/r[ci] for r in z];q=statistics.quantiles(rat,n=4)
  print('STEP5C_MUL_RESULT',opt,'L',L,'median',f'{statistics.median(rat):.9f}','q1',f'{q[0]:.9f}','q3',f'{q[2]:.9f}','aggregate',f'{sum(r[hi] for r in z)/sum(r[ci] for r in z):.9f}',flush=True)
print('STEP5C_LAYER MUL implemented sensitivity L=6,7,8 II=1 shared pipelined multiplier.',flush=True)
print('STEP5C_PENDING control requires explicit predictor/penalty contract; configuration requires cache/discovery cost contract; memory addresses are available but cache hierarchy/latencies require contract; frequency requires measured or declared target periods.',flush=True)
print('STEP5C_RULE no arbitrary values introduced for pending layers.',flush=True)
