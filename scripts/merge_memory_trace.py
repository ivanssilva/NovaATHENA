#!/usr/bin/env python3
import csv,sys,collections
trace,mem,out=sys.argv[1:4]
with open(trace,newline='') as f: rows=list(csv.DictReader(f))
by_pc=collections.defaultdict(list)
with open(mem,newline='') as f:
 for r in csv.DictReader(f):by_pc[int(r['pc'],16)].append(r)
# Pair validated dynamic memory events to dynamic architectural memory instructions by PC occurrence order.
idx=collections.Counter(); matched=0; missing=0; missing_rows=[]
with open(out,'w',newline='') as f:
 w=csv.writer(f);w.writerow(['seq','pc','rw','vaddr','paddr','size','is_io'])
 for r in rows:
  op=r['op'].lower()
  if op not in {'lb','lh','lw','lbu','lhu','sb','sh','sw'}:continue
  pc=int(r['pc'],16);i=idx[pc];idx[pc]+=1
  if i>=len(by_pc[pc]): missing+=1; missing_rows.append(r); continue
  m=by_pc[pc][i];w.writerow([r['seq'],r['pc'],m['rw'],m['vaddr'],m['paddr'],m['size'],m['is_io']]);matched+=1
extra=sum(max(0,len(v)-idx[k]) for k,v in by_pc.items())
print('MEMMERGE matched',matched,'missing',missing,'extra',extra,'trace_memory_ops',matched+missing)
for r in missing_rows: print('MEMMERGE_MISSING',r['seq'],r['pc'],r['op'],r['args'])
ok_shutdown = (missing==1 and missing_rows[0]['pc'].lower()=='0x8000003c' and missing_rows[0]['op'].lower()=='sw' and missing_rows[0]['args'].replace(' ','')=='t1,0(t0)')
if ok_shutdown: print('MEMMERGE_EXCLUDED terminal_harness_store 1')
if extra or (missing and not ok_shutdown): sys.exit(2)
