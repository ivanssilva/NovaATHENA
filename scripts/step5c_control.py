#!/usr/bin/env python3
"""Step 5C control layer: trace-measured branch outcomes and explicit predictors.
No assumed accuracy. Conditional branch outcome is reconstructed from next dynamic PC.
Predictors: always-not-taken and per-PC 2-bit saturating bimodal. Penalty is sensitivity
P=2,4,6,8 cycles, not a measured pipeline parameter. Uses accepted MUL L=6,7,8 results
as cumulative predecessor; reports control penalty separately for later composition.
"""
import csv,glob,os,collections,statistics
BR={'beq','bne','blt','bge','bltu','bgeu'}
def pcint(x): return int(x,0)
paths=sorted(set(glob.glob('structural/*_O*.trace.csv')+glob.glob('structural/**/*.trace.csv',recursive=True))); assert len(paths)==38
out=[]; tot=collections.Counter()
for p in paths:
 name=os.path.basename(p).replace('.trace.csv',''); b,opt=name.rsplit('_',1)
 rr=list(csv.DictReader(open(p))); n=taken=ant_mis=bim_mis=0; state=collections.defaultdict(lambda:1)
 for i,r in enumerate(rr[:-1]):
  op=r['op'].lower()
  if op not in BR: continue
  n+=1; pc=pcint(r['pc']); nxt=pcint(rr[i+1]['pc']); tk=(nxt != pc+4); taken+=tk
  ant_mis+=tk
  pred=state[pc]>=2; bim_mis+=(pred!=tk)
  state[pc]=min(3,state[pc]+1) if tk else max(0,state[pc]-1)
 assert n>0
 tot.update(branches=n,taken=taken,ant_mis=ant_mis,bim_mis=bim_mis)
 out.append((b,opt,n,taken,ant_mis,bim_mis,ant_mis/n,bim_mis/n))
 print('STEP5C_CONTROL_TRACE',name,'branches',n,'taken',taken,'taken_rate',f'{taken/n:.9f}','ANT_mispred',ant_mis,'ANT_rate',f'{ant_mis/n:.9f}','BIM2_mispred',bim_mis,'BIM2_rate',f'{bim_mis/n:.9f}',flush=True)
with open('step5c_control.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['benchmark','opt','conditional_branches','taken','ant_mispred','bimodal2_mispred','taken_rate','bimodal2_mispred_rate']);w.writerows(out)
print('STEP5C_CONTROL_AUDIT traces',len(paths),'branches',tot['branches'],'taken',tot['taken'],'ANT_mispred',tot['ant_mis'],'BIM2_mispred',tot['bim_mis'],flush=True)
for opt in ('O2','O3'):
 z=[r for r in out if r[1]==opt]
 for label,idx in [('ANT',6),('BIM2',7)]:
  v=[r[idx] for r in z];q=statistics.quantiles(v,n=4)
  print('STEP5C_CONTROL_ACCURACY',opt,label,'mispred_median',f'{statistics.median(v):.9f}','q1',f'{q[0]:.9f}','q3',f'{q[2]:.9f}','aggregate',f'{sum(r[4 if label=="ANT" else 5] for r in z)/sum(r[2] for r in z):.9f}',flush=True)
# Penalty events are predictor-specific and can be composed with temporal cycles later.
for P in (2,4,6,8):
 print('STEP5C_CONTROL_PENALTY','P',P,'ANT_cycles',tot['ant_mis']*P,'BIM2_cycles',tot['bim_mis']*P,flush=True)
print('STEP5C_CONTROL_CONTRACT outcome measured from dynamic next-PC; BIM2=per-PC 2-bit saturating counter initialized weakly-not-taken; no BTB capacity/aliasing modeled.',flush=True)
print('STEP5C_CONTROL_SCOPE penalty P=2,4,6,8 is sensitivity, not measured hardware latency; jumps are control boundaries but not charged as conditional-branch mispredictions.',flush=True)
