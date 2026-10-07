#!/usr/bin/env python3
"""Step 5C configuration layer: trace-driven region reuse for ATHENA-L8-C64.
Region = maximal dynamic compute epoch used by the temporal model (ALU/RI/MUL),
bounded by control, memory, DIV/REM, or unsupported operations.
Key = start PC + exact (PC,op,args) region signature, so same start PC with a
different path/body is distinguished. Measures compulsory reuse and C64 under
explicit FIFO and LRU replacement. No hit/miss/generation cycle cost is assumed.
"""
import csv,glob,os,collections,hashlib,json
RR={'add','sub','and','or','xor','sll','srl','sra','slt','sltu'}
RI={'addi','andi','ori','xori','slli','srli','srai','slti','sltiu'}
MUL={'mul','mulh','mulhu','mulhsu'}
COMPUTE=RR|RI|MUL
CAP=64
def regions(rows):
 cur=[]
 for r in rows:
  op=r['op'].lower()
  if op in COMPUTE: cur.append(r)
  else:
   if cur: yield cur; cur=[]
 if cur: yield cur
def key(reg):
 sig=[(r['pc'],r['op'].lower(),r['args']) for r in reg]
 raw=json.dumps(sig,separators=(',',':')).encode()
 return reg[0]['pc']+':'+hashlib.sha256(raw).hexdigest()
def simulate(seq,policy):
 cache=[]; hits=miss=ev=0
 for k in seq:
  if k in cache:
   hits+=1
   if policy=='LRU': cache.remove(k); cache.append(k)
  else:
   miss+=1
   if len(cache)>=CAP: cache.pop(0); ev+=1
   cache.append(k)
 return hits,miss,ev
paths=sorted(set(glob.glob('structural/*_O*.trace.csv')+glob.glob('structural/**/*.trace.csv',recursive=True))); assert len(paths)==38
out=[]; total=collections.Counter()
for p in paths:
 name=os.path.basename(p).replace('.trace.csv',''); b,opt=name.rsplit('_',1)
 rr=list(csv.DictReader(open(p))); regs=list(regions(rr)); seq=[key(x) for x in regs]
 uniq=len(set(seq)); comp=len(seq)-uniq
 fh,fm,fe=simulate(seq,'FIFO'); lh,lm,le=simulate(seq,'LRU')
 assert fh+fm==len(seq) and lh+lm==len(seq)
 total.update(traces=1,regions=len(seq),unique=uniq,fifo_hits=fh,fifo_miss=fm,fifo_ev=fe,lru_hits=lh,lru_miss=lm,lru_ev=le)
 out.append((b,opt,len(seq),uniq,comp,fh,fm,fe,lh,lm,le))
 print('STEP5C_CFG_TRACE',name,'regions',len(seq),'unique',uniq,'ideal_reuse_hits',comp,
       'C64_FIFO_hits',fh,'miss',fm,'evict',fe,'C64_LRU_hits',lh,'miss',lm,'evict',le,flush=True)
with open('step5c_configuration.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['benchmark','opt','regions','unique_regions','ideal_reuse_hits','c64_fifo_hits','c64_fifo_misses','c64_fifo_evictions','c64_lru_hits','c64_lru_misses','c64_lru_evictions']);w.writerows(out)
print('STEP5C_CFG_AUDIT','traces',total['traces'],'regions',total['regions'],'unique_sum',total['unique'],
      'FIFO_hits',total['fifo_hits'],'FIFO_misses',total['fifo_miss'],'LRU_hits',total['lru_hits'],'LRU_misses',total['lru_miss'],flush=True)
for opt in ('O2','O3'):
 z=[r for r in out if r[1]==opt]
 for label,hi,mi in [('FIFO',5,6),('LRU',8,9)]:
  H=sum(r[hi] for r in z); M=sum(r[mi] for r in z)
  print('STEP5C_CFG_RESULT',opt,label,'C',CAP,'hits',H,'misses',M,'hit_rate',f'{H/(H+M) if H+M else 0:.9f}',flush=True)
print('STEP5C_CFG_CONTRACT ATHENA-L8-C64 capacity=64; key=start-PC plus exact region signature; region boundaries reuse Step5C compute epochs.',flush=True)
print('STEP5C_CFG_SCOPE FIFO and LRU are explicit policy sensitivities; no configuration hit/miss/discovery/generation cycle cost is assumed.',flush=True)
