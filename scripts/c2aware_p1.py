#!/usr/bin/env python3
"""OoO4-C2 controlled RAW-pair experiment; compute epochs only, same 5D contract."""
import csv,glob,os,collections
from collections import deque
A={'zero':'x0','ra':'x1','sp':'x2','gp':'x3','tp':'x4','t0':'x5','t1':'x6','t2':'x7','s0':'x8','fp':'x8','s1':'x9','a0':'x10','a1':'x11','a2':'x12','a3':'x13','a4':'x14','a5':'x15','a6':'x16','a7':'x17','s2':'x18','s3':'x19','s4':'x20','s5':'x21','s6':'x22','s7':'x23','s8':'x24','s9':'x25','s10':'x26','s11':'x27','t3':'x28','t4':'x29','t5':'x30','t6':'x31'}
RR={'add','sub','and','or','xor','sll','srl','sra','slt','sltu'}
RI={'addi','andi','ori','xori','slli','srli','srai','slti','sltiu'}
MUL={'mul','mulh','mulhu','mulhsu'}
def dec(op,args):
 a=[A.get(x.strip(),x.strip()) for x in args]
 if op in RR|MUL and len(a)>=3:return (a[0],(a[1],a[2]),op in MUL)
 if op in RI and len(a)>=2:return (a[0],(a[1],),False)
 return None
def simulate(nodes,c2_count=0,rob_size=32,mul_latency=7,policy="P0"):
 n=len(nodes); pred=[set() for _ in nodes];last={}
 for i,(d,src,ismul) in enumerate(nodes):
  for reg in src:
   if reg!='x0' and reg in last:pred[i].add(last[reg])
  if d!='x0':last[d]=i
 dispatched=retired=cyc=0;done={};q=deque();pairs=0;alu_issued=0
 while retired<n:
  count=0
  while q and count<4 and done.get(q[0],10**18)<=cyc:
   q.popleft();retired+=1;count+=1
  slots=min(4,n-dispatched,rob_size-len(q))
  for i in range(dispatched,dispatched+slots):q.append(i)
  dispatched+=slots
  assert len(q)==dispatched-retired and len(q)<=rob_size
  # Select up to four functional-unit slots. One C2 can execute producer+consumer
  # in one cycle, consuming TWO ROB entries, TWO issue instructions, ONE FU slot.
  # Producer must be ready from earlier cycles; consumer must have no other
  # unfinished predecessors and must be dispatched. Pairing is local, no oracle.
  issued_slots=0; c2_used=0; mul_used=False; chosen=set()
  # P1: one locally critical RAW pair is reserved BEFORE oldest-first filling.
  # Both instructions must already be dispatched, not yet issued; the producer
  # is independently ready, while every other consumer predecessor is ready.
  # The rank is a bounded two-hop descendant count within the CURRENT window.
  # It does not inspect future instructions or modify ROB/retirement semantics.
  if policy=="P1" and c2_count:
   window=set(q)
   successors={i:[] for i in q}
   for j in q:
    for p in pred[j]:
     if p in window:successors[p].append(j)
   best=None
   for i in q:
    if i in done or nodes[i][2] or not all(done.get(p,10**18)<=cyc for p in pred[i]):continue
    for j in successors[i]:
     if j in done or nodes[j][2]:continue
     if not all(p==i or done.get(p,10**18)<=cyc for p in pred[j]):continue
     # Two-hop score: direct consumers of j plus their consumers.
     # Count unique successors, ignoring instructions already completed.
     first=[k for k in successors[j] if k not in done]
     second={h for k in first for h in successors[k] if h not in done}
     score=len(first)+len(second)
     candidate=(score,-i,-j,i,j)
     if best is None or candidate>best:best=candidate
   if best is not None:
    i,j=best[-2:]
    done[i]=cyc+1;done[j]=cyc+1
    chosen.add(i);chosen.add(j)
    issued_slots=1;c2_used=1;pairs+=1;alu_issued+=2
  for i in q:
   if issued_slots>=4:break
   if i in done or i in chosen:continue
   if not all(done.get(p,10**18)<=cyc for p in pred[i]):continue
   if nodes[i][2]:
    if mul_used:continue
    mul_used=True;done[i]=cyc+mul_latency;issued_slots+=1;continue
   # Greedy earliest-ready producer, then earliest eligible RAW consumer.
   partner=None
   if c2_used<c2_count and policy=="P0":
    for j in q:
     if j<=i or j in done or j in chosen or nodes[j][2]:continue
     if i not in pred[j]:continue
     if all(p==i or done.get(p,10**18)<=cyc for p in pred[j]):
      partner=j;break
   done[i]=cyc+1;issued_slots+=1;alu_issued+=1
   if partner is not None:
    done[partner]=cyc+1;chosen.add(partner);c2_used+=1;pairs+=1;alu_issued+=1
  cyc+=1
  assert cyc<max(10000,n*20),(n,cyc)
 assert retired==dispatched==n and not q
 return cyc,pairs,alu_issued
def test():
 # Four dependent instructions: 4 cycles baseline, 3 cycles with 1 C2 (dispatch/retire modeled)
 chain=[('x1',('x2',),False),('x3',('x1',),False)]
 assert simulate(chain,0)[0]==3
 assert simulate(chain,1)==(2,1,2)
 assert simulate(chain,2)==(2,1,2)
 indep=[('x1',('x2',),False),('x3',('x4',),False)]
 assert simulate(indep,0)[0]==simulate(indep,2)[0]
 # WAR is NOT a pairing opportunity; RAW on independent renamed values only.
 war=[('x2',('x1',),False),('x1',('x3',),False)]
 assert simulate(war,2)[1]==0
 # two independent chains, both eligible same cycle
 two=[('x1',('x2',),False),('x3',('x1',),False),('x4',('x5',),False),('x6',('x4',),False)]
 assert simulate(two,2)[1]==2
 assert simulate(two,1)[1]==1
 assert simulate(two,1,policy='P1')[1]==1
 assert simulate(chain,1,policy='P1')==(2,1,2)
 assert simulate(war,1,policy='P1')[1]==0
 # older non-paired MUL is still constrained to one per cycle
 mul=[('x1',('x2','x3'),True),('x4',('x5','x6'),True)]
 assert simulate(mul,2)[1]==0
 print('C2AWARE_SELFTEST_PASS',flush=True)
test()
paths=sorted(set(glob.glob('structural/*_O*.trace.csv')+glob.glob('structural/**/*.trace.csv',recursive=True)))
assert len(paths)==38,len(paths)
prior=glob.glob('inputs/**/step5c_cumulative.csv',recursive=True);assert len(prior)==1,prior
cumulative=list(csv.DictReader(open(prior[0])))
base={(x['benchmark'],x['opt']):x for x in cumulative if x['mul_latency']=='7' and x['branch_penalty']=='4' and x['l1_kib']=='32' and x['ways']=='4' and x['cfg_hit_cost']=='0' and x['cfg_miss_cost']=='4' and x['l1_miss_penalty']=='50'}
assert len(base)==38,len(base)
results=[]
for p in paths:
 name=os.path.basename(p).replace('.trace.csv','');b,opt=name.rsplit('_',1)
 epochs=[];cur=[]
 for r in csv.DictReader(open(p)):
  x=dec(r['op'].lower(),r['args'].split(','))
  if x:cur.append(x)
  elif cur:epochs.append(cur);cur=[]
 if cur:epochs.append(cur)
 common=int(base[(b,opt)]['bim2_control_cycles'])+int(base[(b,opt)]['l1_miss_cycles'])
 p0_compute=p0_pairs=p1_compute=p1_pairs=0
 for e in epochs:
  a=simulate(e,1,policy='P0');z=simulate(e,1,policy='P1')
  p0_compute+=a[0];p0_pairs+=a[1]
  p1_compute+=z[0];p1_pairs+=z[1]
 for policy,compute,pairs in [('P0',p0_compute,p0_pairs),('P1',p1_compute,p1_pairs)]:
  results.append(dict(benchmark=b,opt=opt,policy=policy,epochs=len(epochs),compute_cycles=compute,common_cycles=common,total_cycles=compute+common,raw_pairs=pairs))
 print('C2AWARE_TRACE',name,'epochs',len(epochs),'P0',p0_compute,p0_pairs,'P1',p1_compute,p1_pairs,flush=True)
with open('c2aware_p0_p1.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
for opt in ('O2','O3'):
 group=[r for r in results if r['opt']==opt]
 a=[r for r in group if r['policy']=='P0'];b=[r for r in group if r['policy']=='P1']
 assert len(a)==len(b)==19
 for kind in ('compute_cycles','total_cycles'):
  ref=sum(r[kind] for r in a);new=sum(r[kind] for r in b)
  print('C2AWARE_RESULT',opt,kind,'P0',ref,'P1',new,'speedup',f'{ref/new:.9f}',flush=True)
 print('C2AWARE_PAIRS',opt,'P0',sum(r['raw_pairs'] for r in a),'P1',sum(r['raw_pairs'] for r in b),flush=True)
 print('C2AWARE_BENCH',opt,'better',sum(bi['total_cycles']<ai['total_cycles'] for ai,bi in zip(a,b)),'worse',sum(bi['total_cycles']>ai['total_cycles'] for ai,bi in zip(a,b)),flush=True)
print('C2AWARE_LIMIT same compute epochs; no continuous memory/control ROB; P1 2-hop window-local priority only',flush=True)
