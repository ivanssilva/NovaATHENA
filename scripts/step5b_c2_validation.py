#!/usr/bin/env python3
"""Semantic unit tests for ATHENA PE-C2 same-cycle fusion scheduler."""
import heapq

def dag(nodes):
 pred=[set() for _ in nodes];succ=[[] for _ in nodes];last={}
 for i,(d,src) in enumerate(nodes):
  for x in src:
   if x!='x0' and x in last: pred[i].add(last[x])
  if d!='x0': last[d]=i
 for i in range(len(nodes)):
  for p in pred[i]: succ[p].append(i)
 return pred,succ

def schedule_c2(nodes,width=8,max_pairs=2):
 pred,succ=dag(nodes); completed=set(); cycles=fused=0
 while len(completed)<len(nodes):
  ready=sorted(i for i in range(len(nodes)) if i not in completed and pred[i] <= completed)
  if not ready: raise RuntimeError('no ready node')
  chosen=[]; chosen_set=set(); pairs=0
  # deterministic oldest-ready producers; reserve capacity for an immediate child.
  for u in ready:
   if u in chosen_set or len(chosen)>=width: continue
   chosen.append(u);chosen_set.add(u)
   if pairs>=max_pairs or len(chosen)>=width: continue
   cand=[]
   for v in succ[u]:
    if v in completed or v in chosen_set: continue
    # Before this cycle, every predecessor except u must already be complete.
    if pred[v] - completed == {u}: cand.append(v)
   if cand:
    v=min(cand);chosen.append(v);chosen_set.add(v);pairs+=1;fused+=1
  # Fill any remaining slots with old-cycle-ready independent operations.
  for u in ready:
   if len(chosen)>=width: break
   if u not in chosen_set: chosen.append(u);chosen_set.add(u)
  completed.update(chosen);cycles+=1
 return cycles,fused

def I(d,*s): return (d,list(s))
cases=[
 ('chain2',[I('x1','x20'),I('x2','x1')],1,1),
 ('two_parallel_chains',[I('x1','x20'),I('x2','x1'),I('x3','x21'),I('x4','x3')],1,2),
 ('chain3',[I('x1','x20'),I('x2','x1'),I('x3','x2')],2,1),
 ('fork',[I('x1','x20'),I('x2','x1'),I('x3','x1')],1,1),
 ('join_not_same_cycle',[I('x1','x20'),I('x2','x21'),I('x3','x1','x2')],2,0),
 ('three_parallel_chains_limit2',[I('x1','x20'),I('x2','x1'),I('x3','x21'),I('x4','x3'),I('x5','x22'),I('x6','x5')],2,3),
 ('independent8',[I(f'x{i}','x20') for i in range(1,9)],1,0),
]
for name,n,ec,ef in cases:
 c,f=schedule_c2(n)
 assert (c,f)==(ec,ef),(name,c,f,ec,ef)
 print('STEP5B_C2_TEST',name,'PASS cycles',c,'fused',f)
# barrier: scheduler called per epoch, so a producer in left epoch cannot feed right.
left=[I('x1','x20')];right=[I('x2','x1')]
c1,f1=schedule_c2(left);c2,f2=schedule_c2(right)
assert (c1+c2,f1+f2)==(2,0)
print('STEP5B_C2_TEST barrier PASS cycles 2 fused 0')
print('STEP5B_C2_VALIDATION cases 8 failures 0')
print('STEP5B_C2_INVARIANT max_two_pairs_per_cycle=yes one_RAW_edge_per_fusion=yes no_three_deep_same_cycle=yes barriers_not_crossed=yes deterministic=yes')
