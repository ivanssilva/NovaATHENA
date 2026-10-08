#!/usr/bin/env python3
"""Step 5C closure: clock-ratio break-even from accepted cumulative sensitivity.
No processor clock is inferred from standalone combinational paths.
"""
import csv,glob,collections
p=glob.glob('inputs/**/step5c_cumulative.csv',recursive=True);assert len(p)==1,p
r=list(csv.DictReader(open(p[0])));assert len(r)==16416,len(r)
out=[]
for x in r:
 h=float(x['h4_total']);a=float(x['athena_total']);q=h/a
 out.append([x['benchmark'],x['opt'],x['mul_latency'],x['branch_penalty'],x['l1_kib'],x['ways'],x['cfg_hit_cost'],x['cfg_miss_cost'],x['l1_miss_penalty'],q,q])
with open('step5c_clock_break_even.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['benchmark','opt','mul_latency','branch_penalty','l1_kib','ways','cfg_hit_cost','cfg_miss_cost','l1_miss_penalty','max_athena_clock_period_over_h4','same_clock_cycle_ratio']);w.writerows(out)
print('STEP5C_CLOCK_AUDIT scenarios',len(out),'benchmarks',len(set((x[0],x[1]) for x in out)),flush=True)
for opt in ('O2','O3'):
 for H,M in ((0,4),(0,16),(1,8),(1,16)):
  z=[x for x in r if x['opt']==opt and x['mul_latency']=='7' and x['branch_penalty']=='4' and x['l1_kib']=='32' and x['ways']=='4' and x['cfg_hit_cost']==str(H) and x['cfg_miss_cost']==str(M) and x['l1_miss_penalty']=='50']
  assert len(z)==19
  h=sum(int(x['h4_total']) for x in z);a=sum(int(x['athena_total']) for x in z);q=h/a
  print('STEP5C_CLOCK_RESULT',opt,'H',H,'M',M,'break_even_Tathena_over_Th4',f'{q:.9f}','athena_max_clock_slowdown_pct',f'{(q-1)*100:.4f}',flush=True)
print('STEP5C_CLOCK_PHYSICAL_REFERENCE PE_ALU 1.3127ns PE_C2 1.9491ns K5 4.0186ns mapped unconstrained combinational; NOT processor clock periods.',flush=True)
print('STEP5C_CLOCK_CONTRACT ATHENA wins in time iff T_ATHENA/T_H4 < C_H4/C_ATHENA; no inferred system frequency or physical speedup.',flush=True)
