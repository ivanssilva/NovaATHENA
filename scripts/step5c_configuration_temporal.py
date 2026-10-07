#!/usr/bin/env python3
"""Step 5C configuration temporal sensitivity.
Consumes measured C64 region reuse conceptually: recomputes the same deterministic
trace-driven FIFO/LRU events, then reports overhead = hits*H + misses*M.
H and M are declared sensitivity parameters, not measured latencies.
No claim of final speedup is made.
"""
import csv,glob,os,hashlib,json,collections
RR={'add','sub','and','or','xor','sll','srl','sra','slt','sltu'}
RI={'addi','andi','ori','xori','slli','srli','srai','slti','sltiu'}
MUL={'mul','mulh','mulhu','mulhsu'}; COMPUTE=RR|RI|MUL; CAP=64
def regs(rows):
 c=[]
 for r in rows:
  if r['op'].lower() in COMPUTE:c.append(r)
  else:
   if c:yield c;c=[]
 if c:yield c
def key(g):
 raw=json.dumps([(r['pc'],r['op'].lower(),r['args']) for r in g],separators=(',',':')).encode()
 return g[0]['pc']+':'+hashlib.sha256(raw).hexdigest()
def sim(seq,pol):
 c=[];h=m=0
 for k in seq:
  if k in c:
   h+=1
   if pol=='LRU':c.remove(k);c.append(k)
  else:
   m+=1
   if len(c)>=CAP:c.pop(0)
   c.append(k)
 return h,m
paths=sorted(set(glob.glob('structural/*_O*.trace.csv')+glob.glob('structural/**/*.trace.csv',recursive=True)));assert len(paths)==38
rows=[];tot=collections.Counter()
for p in paths:
 name=os.path.basename(p).replace('.trace.csv','');b,opt=name.rsplit('_',1)
 seq=[key(g) for g in regs(list(csv.DictReader(open(p))))]
 fh,fm=sim(seq,'FIFO');lh,lm=sim(seq,'LRU')
 rows.append((b,opt,len(seq),fh,fm,lh,lm));tot.update(regions=len(seq),fifo_h=fh,fifo_m=fm,lru_h=lh,lru_m=lm)
with open('step5c_configuration_temporal.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['benchmark','opt','regions','fifo_hits','fifo_misses','lru_hits','lru_misses']);w.writerows(rows)
print('STEP5C_CFGT_AUDIT traces',len(rows),'regions',tot['regions'],'FIFO_hits',tot['fifo_h'],'FIFO_misses',tot['fifo_m'],'LRU_hits',tot['lru_h'],'LRU_misses',tot['lru_m'],flush=True)
# Explicit sensitivity grid. H=0/1/2; miss generation cost M=4/8/16/32/64 cycles.
for opt in ('O2','O3'):
 z=[r for r in rows if r[1]==opt]
 for pol,hi,mi in [('FIFO',3,4),('LRU',5,6)]:
  HN=sum(r[hi] for r in z);MN=sum(r[mi] for r in z)
  for H in (0,1,2):
   for M in (4,8,16,32,64):
    ov=HN*H+MN*M
    print('STEP5C_CFGT_SENS',opt,pol,'H',H,'M',M,'overhead_cycles',ov,'per_region',f'{ov/sum(r[2] for r in z):.9f}',flush=True)
print('STEP5C_CFGT_FORMULA overhead_cycles = hits*H + misses*M.',flush=True)
print('STEP5C_CFGT_SCOPE H={0,1,2} and M={4,8,16,32,64} are sensitivity points only, not measured ATHENA latencies.',flush=True)
print('STEP5C_CFGT_RULE no sensitivity point is promoted to a hardware measurement or final speedup.',flush=True)
