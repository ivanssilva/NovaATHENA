#!/usr/bin/env python3
import csv,sys,collections
trace,mem,out=sys.argv[1:4]
with open(trace,newline='') as f: rows=list(csv.DictReader(f))
by_pc=collections.defaultdict(list)
with open(mem,newline='') as f:
 for r in csv.DictReader(f):by_pc[int(r['pc'],16)].append(r)
# Pair dynamic memory events to dynamic architectural memory instructions by PC occurrence order.
idx=collections.Counter(); matched=0; missing=0
with open(out,'w',newline='') as f:
 w=csv.writer(f);w.writerow(['seq','pc','rw','vaddr','paddr','size','is_io'])
 for r in rows:
  op=r['op'].lower()
  if op not in {'lb','lh','lw','lbu','lhu','sb','sh','sw'}:continue
  pc=int(r['pc'],16);i=idx[pc];idx[pc]+=1
  if i>=len(by_pc[pc]):missing+=1;continue
  m=by_pc[pc][i];w.writerow([r['seq'],r['pc'],m['rw'],m['vaddr'],m['paddr'],m['size'],m['is_io']]);matched+=1
extra=sum(max(0,len(v)-idx[k]) for k,v in by_pc.items())
print('MEMMERGE matched',matched,'missing',missing,'extra',extra,'trace_memory_ops',matched+missing)
if missing or extra:sys.exit(2)
