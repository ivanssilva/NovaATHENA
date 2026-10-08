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
def simulate(nodes,c2_count=0,rob_size=32,mul_latency=7):
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
  for i in q:
   if issued_slots>=4:break
   if i in done or i in chosen:continue
   if not all(done.get(p,10**18)<=cyc for p in pred[i]):continue
   if nodes[i][2]:
    if mul_used:continue
    mul_used=True;done[i]=cyc+mul_latency;issued_slots+=1;continue
   # Greedy earliest-ready producer, then earliest eligible RAW consumer.
   partner=None
   if c2_used<c2_count:
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
 # older non-paired MUL is still constrained to one per cycle
 mul=[('x1',('x2','x3'),True),('x4',('x5','x6'),True)]
 assert simulate(mul,2)[1]==0
 print('OOOC2_SELFTEST_PASS',flush=True)
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
 metrics=[tuple(map(sum,zip(*(simulate(e,k) for e in epochs)))) for k in (0,1,2)]
 values=[m[0] for m in metrics]
 pairs=[metrics[1][1],metrics[2][1]]
 assert values[0]>=min(values)
 for k,pc in [(0,0),(1,pairs[0]),(2,pairs[1])]:
  total=values[k]+common
  results.append(dict(benchmark=b,opt=opt,c2_units=k,epochs=len(epochs),compute_cycles=values[k],common_cycles=common,total_cycles=total,raw_pairs=pc,ratio_cycles=0))
 print('OOOC2_TRACE',name,'epochs',len(epochs),'compute',*values,'pairs',*pairs,flush=True)
# compare against original 5D values, same simulator contract
for b in set((r['benchmark'],r['opt']) for r in results):
 group=[r for r in results if (r['benchmark'],r['opt'])==b]
 ref=next(r['total_cycles'] for r in group if r['c2_units']==0)
 for r in group:r['ratio_cycles']=ref/r['total_cycles']
with open('ooo4_c2_results.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
for opt in ('O2','O3'):
 group=[r for r in results if r['opt']==opt]
 ref=sum(r['total_cycles'] for r in group if r['c2_units']==0)
 for k in (1,2):
  z=[r for r in group if r['c2_units']==k]
  ratio=ref/sum(r['total_cycles'] for r in z)
  print('OOOC2_RESULT',opt,'c2_units',k,'cycle_ratio',f'{ratio:.9f}','raw_pairs',sum(r['raw_pairs'] for r in z),'better_benchmarks',sum(r['ratio_cycles']>1 for r in z),flush=True)
  for t in (1,1.25,1.5,2):
   print('OOOC2_CLOCK',opt,'c2_units',k,'period_ratio',t,'time_speedup',f'{ratio/t:.9f}',flush=True)
print('OOOC2_LIMIT compute epochs only; common memory/control additive; no full CPU clock, LSQ, physical implementation, or cost of pair detection',flush=True)
