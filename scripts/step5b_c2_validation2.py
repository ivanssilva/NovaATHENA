#!/usr/bin/env python3
"""Independent analytical validation of Step 5B C2 same-cycle fusion semantics."""
def dag(nodes):
 p=[set() for _ in nodes];s=[[] for _ in nodes];last={}
 for i,(d,src) in enumerate(nodes):
  for r in src:
   if r!='x0' and r in last:p[i].add(last[r])
  if d!='x0':last[d]=i
 for i in range(len(nodes)):
  for u in p[i]:s[u].append(i)
 return p,s
def sched(nodes,width=8,npairs=2):
 p,s=dag(nodes);done=set();cycles=0;fusions=0;maxf=0
 while len(done)<len(nodes):
  ready=[i for i in range(len(nodes)) if i not in done and p[i]<=done]
  chosen=[];used=set();fc=0
  for u in ready:
   if len(chosen)>=width:break
   if u in used:continue
   chosen.append(u);used.add(u)
   if fc<npairs and len(chosen)<width:
    # A C2 consumer may be admitted only when its sole unsatisfied
    # dependency at cycle start is producer u.
    cand=[vv for vv in s[u] if vv not in done and vv not in used and (p[vv]-done)=={u}]
    if cand:
     vv=min(cand);chosen.append(vv);used.add(vv);fc+=1
  assert chosen
  done.update(chosen);cycles+=1;fusions+=fc;maxf=max(maxf,fc)
  assert fc<=npairs
 return cycles,fusions,maxf
R=lambda d,*s:(d,list(s))
cases=[
 ('chain2',[R('x1','x2'),R('x3','x1')],(1,1)),
 ('two_chains',[R('x1','x10'),R('x2','x1'),R('x3','x11'),R('x4','x3')],(1,2)),
 # With three chains and only two C2 pairs, the third producer can still
 # execute in cycle 1 as a normal operation. Its consumer is ready in cycle 2.
 # Thus the minimum is two cycles, but only two same-cycle fusions are required.
 ('three_chains_pair_limit',[R('x1','x10'),R('x2','x1'),R('x3','x11'),R('x4','x3'),R('x5','x12'),R('x6','x5')],(2,2)),
 ('chain3',[R('x1','x10'),R('x2','x1'),R('x3','x2')],(2,1)),
 ('fork',[R('x1','x10'),R('x2','x1'),R('x3','x1')],(2,1)),
 ('join',[R('x1','x10'),R('x2','x11'),R('x3','x1','x2')],(2,0)),
 ('independent8',[R(f'x{i+1}',f'x{i+10}') for i in range(8)],(1,0)),
 ('independent_plus_chain',[R('x1','x10'),R('x2','x1')]+[R(f'x{i}',f'x{i+10}') for i in range(3,9)],(1,1)),
]
fail=0
for name,nodes,exp in cases:
 c,f,m=sched(nodes);ok=(c,f)==exp;fail+=not ok
 print('STEP5B_C2_VALIDATION',name,'cycles',c,'fusions',f,'max_fusions_cycle',m,'expected',exp,'PASS' if ok else 'FAIL')
print('STEP5B_C2_VALIDATION_SUMMARY cases',len(cases),'failures',fail)
assert fail==0
