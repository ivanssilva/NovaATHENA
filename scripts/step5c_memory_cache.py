#!/usr/bin/env python3
"""Step 5C memory/cache characterization from definitive enriched traces.
Cacheable effective-address accesses only; I/O excluded and reported separately.
LRU, write-allocate data cache. 64-B lines. Sensitivity only: 16/32/64 KiB and
1/2/4-way. No cache/memory latency is assumed here.
"""
import csv,glob,os,collections
LINE=64
CASES=[(k,w) for k in (16,32,64) for w in (1,2,4)]
def getaddr(r):
 for k in ('vaddr','va','effective_address','effective_addr','address','addr'):
  if k in r and r[k] not in ('',None):
   try:return int(r[k],0)
   except:pass
 raise KeyError('no address field '+str(list(r)))
def isio(r):
 for k in ('io','is_io','iomem'):
  if k in r:
   return str(r[k]).strip().lower() in ('1','true','yes','y')
 return False
def sim(addrs,kib,ways):
 sets=(kib*1024)//(LINE*ways); assert sets>0
 c=[[] for _ in range(sets)];h=m=0
 for a in addrs:
  b=a//LINE;s=b%sets;t=b//sets
  q=c[s]
  if t in q:q.remove(t);q.append(t);h+=1
  else:
   m+=1
   if len(q)>=ways:q.pop(0)
   q.append(t)
 return h,m
paths=sorted(glob.glob('memory/**/*.csv',recursive=True)+glob.glob('memory/*.csv'))
# retain only likely enriched trace CSVs, identified by readable address column
valid=[]
for p in paths:
 try:
  with open(p,newline='') as f:
   rd=csv.DictReader(f); first=next(rd,None)
  if first is not None:
   getaddr(first);valid.append(p)
 except:pass
# deduplicate basenames/paths if artifact contains nested duplicates
by={}
for p in valid: by[os.path.basename(p)]=p
paths=sorted(by.values()); assert len(paths)==38,(len(paths),paths[:10])
out=[]; totals=collections.Counter()
for p in paths:
 name=os.path.basename(p)
 for suf in ('.trace.enriched.csv','.enriched.csv','.trace.csv','.memory.csv','.csv'):
  if name.endswith(suf):name=name[:-len(suf)];break
 try:b,opt=name.rsplit('_',1)
 except: b,opt=name,'NA'
 assert opt in ('O2','O3'),(p,name,opt)
 add=[];io=0;reads=writes=0
 with open(p,newline='') as f:
  for r in csv.DictReader(f):
   if isio(r):io+=1;continue
   add.append(getaddr(r))
   op=str(r.get('mem_op',r.get('rw',r.get('access','')))).upper()
   if op.startswith('R'):reads+=1
   elif op.startswith('W'):writes+=1
 totals.update(traces=1,accesses=len(add),io=io)
 for kib,ways in CASES:
  h,m=sim(add,kib,ways);assert h+m==len(add)
  out.append((b,opt,kib,ways,len(add),io,h,m,h/(h+m) if h+m else 0))
  print('STEP5C_MEM_TRACE',name,'C',kib,'KiB','W',ways,'accesses',len(add),'io_excluded',io,'hits',h,'misses',m,'miss_rate',f'{m/(h+m) if h+m else 0:.9f}',flush=True)
with open('step5c_memory_cache.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['benchmark','opt','capacity_kib','ways','cacheable_accesses','io_excluded','hits','misses','hit_rate']);w.writerows(out)
print('STEP5C_MEM_AUDIT traces',totals['traces'],'cacheable_accesses',totals['accesses'],'io_excluded',totals['io'],flush=True)
for opt in ('O2','O3'):
 for kib,ways in CASES:
  z=[r for r in out if r[1]==opt and r[2]==kib and r[3]==ways]
  assert len(z)==19,(opt,kib,ways,len(z))
  h=sum(r[6] for r in z);m=sum(r[7] for r in z)
  print('STEP5C_MEM_RESULT',opt,'C',kib,'KiB','W',ways,'hits',h,'misses',m,'miss_rate',f'{m/(h+m):.9f}',flush=True)
print('STEP5C_MEM_CONTRACT L1D sensitivity: 64-B line, LRU, write-allocate, capacities 16/32/64 KiB, associativity 1/2/4; effective addresses from definitive Step5A traces.',flush=True)
print('STEP5C_MEM_SCOPE I/O accesses excluded from cache simulation and counted separately; no cache-hit or lower-memory latency is assumed.',flush=True)
print('STEP5C_MEM_RULE cache organizations are sensitivity points, not a declared final ATHENA cache.',flush=True)
