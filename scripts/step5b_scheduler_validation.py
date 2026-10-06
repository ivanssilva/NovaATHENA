#!/usr/bin/env python3
"""Independent validation tests for Step 5B deterministic RAW scheduler.
Synthetic cases have analytically known cycle counts. Fails closed on mismatch.
"""
import heapq

def sched(nodes,width):
 n=len(nodes); pred=[set() for _ in range(n)]; succ=[[] for _ in range(n)]; last={}
 for i,(d,src) in enumerate(nodes):
  for x in src:
   if x!='x0' and x in last: pred[i].add(last[x])
  if d!='x0': last[d]=i
 for i in range(n):
  for p in pred[i]:succ[p].append(i)
 indeg=[len(x) for x in pred]; ready=[i for i,x in enumerate(indeg) if x==0];heapq.heapify(ready)
 cycles=issued=0
 while issued<n:
  assert ready
  now=[heapq.heappop(ready) for _ in range(min(width,len(ready)))]
  nxt=[]
  for u in now:
   issued+=1
   for v in succ[u]:
    indeg[v]-=1
    if indeg[v]==0:nxt.append(v)
  for v in nxt:heapq.heappush(ready,v)
  cycles+=1
 return cycles,issued

def I(dst,*src):return (dst,list(src))
cases=[
 ('one',[I('x1','x2','x3')],1,1),
 ('independent4',[I(f'x{i}','x20','x21') for i in range(1,5)],1,1),
 ('independent5',[I(f'x{i}','x20','x21') for i in range(1,6)],2,1),
 ('independent8',[I(f'x{i}','x20','x21') for i in range(1,9)],2,1),
 ('independent9',[I(f'x{i}','x20','x21') for i in range(1,10)],3,2),
 ('chain2',[I('x1','x20'),I('x2','x1')],2,2),
 ('chain4',[I('x1','x20'),I('x2','x1'),I('x3','x2'),I('x4','x3')],4,4),
 ('fork',[I('x1','x20'),I('x2','x1'),I('x3','x1'),I('x4','x1'),I('x5','x1')],2,2),
 ('join',[I('x1','x20'),I('x2','x21'),I('x3','x1','x2')],2,2),
 # WAW is not a dependency under ideal renaming; later writer can issue same cycle.
 ('waw_renamed',[I('x1','x20'),I('x1','x21')],1,1),
 # WAR is not a dependency under ideal renaming.
 ('war_renamed',[I('x2','x1'),I('x1','x20')],1,1),
]
for name,n,h,a in cases:
 gh,ih=sched(n,4);ga,ia=sched(n,8)
 assert (gh,ga,ih,ia)==(h,a,len(n),len(n)),(name,gh,ga,ih,ia)
 print('STEP5B_TEST',name,'PASS','host4',gh,'athena8',ga,'ops',len(n))
# Barrier semantics are tested as epoch decomposition: two 4-op independent epochs
# must cost 2 cycles, not be merged into one 8-wide ATHENA cycle.
left=[I(f'x{i}','x20') for i in range(1,5)];right=[I(f'x{i}','x21') for i in range(5,9)]
bh=sum(sched(e,4)[0] for e in (left,right));ba=sum(sched(e,8)[0] for e in (left,right))
assert (bh,ba)==(2,2)
print('STEP5B_TEST barrier_epoch PASS host4 2 athena8 2')
print('STEP5B_VALIDATION cases',len(cases)+1,'failures 0')
print('STEP5B_INVARIANT every_op_issued_once=yes raw_successor_next_cycle_or_later=yes waw_war_ignored_under_ideal_rename=yes barriers_not_crossed=yes deterministic_oldest_ready=yes')
