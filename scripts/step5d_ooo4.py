#!/usr/bin/env python3
"""5D finite-ROB OOO-4 compute-epoch reference. Memory/control are common additive
sensitivities from 5C, not a complete OoO LSQ or coupled timing simulator."""
import csv,glob,os,collections
from collections import deque
#/usr/bin/env python3
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

def ooo(nodes,rob_size=32,mul_latency=7):
 # 4 dispatch, 4 issue, 4 retire; 4 simple ALUs, 1 shared pipelined MUL II=1.
 # True RAW via latest producer, in-order retirement; 32-entry ROB.
 n=len(nodes);pred=[set() for _ in nodes];last={}
 for i,(d,src,im) in enumerate(nodes):
  for reg in src:
   if reg!='x0' and reg in last:pred[i].add(last[reg])
  if d!='x0':last[d]=i
 dispatched=retired=cyc=0;done={};queue=deque()
 while retired<n:
  # retire only previously completed oldest instructions
  count=0
  while queue and count<4 and done.get(queue[0],10**18)<=cyc:
   queue.popleft();retired+=1;count+=1
  slots=min(4,n-dispatched,rob_size-len(queue))
  assert slots>=0,(n,dispatched,retired,len(queue))
  for i in range(dispatched,dispatched+slots):
   queue.append(i)
  dispatched+=slots
  assert len(queue)==dispatched-retired and len(queue)<=rob_size
  assert len(set(queue))==len(queue)
  issued=0;mul_used=False
  for i in queue:
   if issued>=4:break
   if i in done:continue
   if nodes[i][2] and mul_used:continue
   if all(done.get(p,10**18)<=cyc for p in pred[i]):
    done[i]=cyc+(mul_latency if nodes[i][2] else 1)
    issued+=1;mul_used|=nodes[i][2]
  cyc+=1
  assert cyc<max(10000,n*20),(n,cyc)
 assert retired==dispatched==n and not queue
 return cyc
paths=sorted(set(glob.glob('structural/*_O*.trace.csv')+glob.glob('structural/**/*.trace.csv',recursive=True)))
assert len(paths)==38,len(paths)
prior=glob.glob('inputs/**/step5c_cumulative.csv',recursive=True);assert len(prior)==1,prior
cumulative=list(csv.DictReader(open(prior[0])))
base={(x['benchmark'],x['opt']):x for x in cumulative if x['mul_latency']=='7' and x['branch_penalty']=='4' and x['l1_kib']=='32' and x['ways']=='4' and x['cfg_hit_cost']=='0' and x['cfg_miss_cost']=='4' and x['l1_miss_penalty']=='50'}
assert len(base)==38,len(base)
results=[]
for p in paths:
 name=os.path.basename(p).replace('.trace.csv','');b,opt=name.rsplit('_',1);epochs=[];cur=[]
 for r in csv.DictReader(open(p)):
  q=dec(r['op'].lower(),[x.strip() for x in r['args'].split(',') if x.strip()])
  if q:cur.append(q)
  else:
   if cur:epochs.append(cur);cur=[]
 if cur:epochs.append(cur)
 cycles=sum(ooo(e) for e in epochs)
 z=base[(b,opt)]
 # common penalty same trace; configuration only ATHENA, from accepted 5C
 common=int(z['bim2_control_cycles'])+int(z['l1_miss_cycles'])
 ooo_total=cycles+common;ath=int(z['athena_total'])
 results.append((b,opt,len(epochs),cycles,common,ooo_total,ath,ooo_total/ath))
 print('STEP5D_TRACE',name,'epochs',len(epochs),'ooo_compute',cycles,'ooo_total',ooo_total,'athena_total',ath,'ratio_same_clock',f'{ooo_total/ath:.9f}',flush=True)
with open('step5d_ooo4.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['benchmark','opt','compute_epochs','ooo4_compute_cycles','common_control_memory_cycles','ooo4_partial_total','athena_5c_total','ratio_same_clock']);w.writerows(results)
print('STEP5D_AUDIT traces',len(results),'scenarios 1','rob 32','dispatch 4','issue 4','retire 4','alu 4','mul 1','mul_latency 7',flush=True)
for opt in ('O2','O3'):
 z=[x for x in results if x[1]==opt];assert len(z)==19
 print('STEP5D_RESULT',opt,'aggregate_ratio_same_clock',f'{sum(x[5] for x in z)/sum(x[6] for x in z):.9f}','athena_lower_cycles_benchmarks',sum(x[6]<x[5] for x in z),flush=True)
print('STEP5D_LIMIT finite ROB model only for compute epochs; memory, branch, and unsupported instruction timing not explicitly scheduled; no LSQ, speculative memory, port contention, or frequency. Do not claim complete OoO speedup.',flush=True)
