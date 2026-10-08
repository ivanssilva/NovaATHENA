#!/usr/bin/env python3
"""Cumulative 5C sensitivity from accepted per-benchmark artifacts; no measured timing."""
import csv,glob,os
def read(pattern):
 p=glob.glob(pattern,recursive=True);assert len(p)==1,(pattern,p)
 return {(r['benchmark'],r['opt']):r for r in csv.DictReader(open(p[0]))}
mul=read('inputs/**/step5c_progressive.csv');ctl=read('inputs/**/step5c_control.csv');cfg=read('inputs/**/step5c_configuration_temporal.csv');mem=read('inputs/**/step5c_memory_cache.csv') if False else None
mfiles=glob.glob('inputs/**/step5c_memory_cache.csv',recursive=True);assert len(mfiles)==1,mfiles
memory={(r['benchmark'],r['opt'],int(r['capacity_kib']),int(r['ways'])):r for r in csv.DictReader(open(mfiles[0]))}
assert len(mul)==len(ctl)==len(cfg)==38 and len(memory)==342,(len(mul),len(ctl),len(cfg),len(memory))
out=[]
for k in sorted(mul):
 a,b,c=mul[k],ctl[k],cfg[k]
 for L in (6,7,8):
  baseh=int(a[f'L{L}_H4']);basec=int(a[f'L{L}_C2'])
  for P in (2,4,6,8):
   control=int(b['bimodal2_mispred'])*P
   for cap,ways in ((16,2),(32,4),(64,2)):
    m=memory[k+(cap,ways)];miss=int(m['misses'])
    for H,M in ((0,4),(0,16),(1,8),(1,16)):
     ch=int(c['lru_hits']);cm=int(c['lru_misses']);conf=ch*H+cm*M
     for penalty in (10,50,100):
      memcost=miss*penalty
      # Symmetric memory and predictor costs; configuration charged only ATHENA.
      h=baseh+control+memcost;ath=basec+control+memcost+conf
      out.append([*k,L,P,cap,ways,H,M,penalty,baseh,basec,control,ch,cm,conf,miss,memcost,h,ath,h/ath if ath else 0,baseh-basec-conf])
with open('step5c_cumulative.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['benchmark','opt','mul_latency','branch_penalty','l1_kib','ways','cfg_hit_cost','cfg_miss_cost','l1_miss_penalty','h4_mul_cycles','athena_mul_cycles','bim2_control_cycles','cfg_hits','cfg_misses','cfg_cycles','l1_misses','l1_miss_cycles','h4_total','athena_total','ratio_same_clock','compute_cfg_margin']);w.writerows(out)
print('STEP5C_CUM_AUDIT benchmarks',len(mul),'scenarios',len(out),'memory_rows',len(memory),flush=True)
for opt in ('O2','O3'):
 for H,M in ((0,4),(0,16),(1,8),(1,16)):
  z=[r for r in out if r[1]==opt and r[2]==7 and r[3]==4 and r[4]==32 and r[5]==4 and r[6]==H and r[7]==M and r[8]==50]
  assert len(z)==19
  sh=sum(r[17] for r in z);sa=sum(r[18] for r in z)
  print('STEP5C_CUM_RESULT',opt,'L7 P4 L1_32KiB_4way misspen50','H',H,'M',M,'ratio_same_clock',f'{sh/sa:.9f}','athena_lower_cycles_benchmarks',sum(r[18]<r[17] for r in z),flush=True)
print('STEP5C_CUM_CONTRACT additive serialized upper-overhead sensitivity; predictor and memory miss penalties symmetric; configuration charged only ATHENA.',flush=True)
print('STEP5C_CUM_LIMIT not a coupled issue/ROB/cache timing simulation; excludes L1 hit latency, memory-level parallelism, overlapping config, I/O, and clock differences. No physical speedup claim.',flush=True)
