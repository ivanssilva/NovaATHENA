#!/usr/bin/env python3
"""Parse QEMU -d in_asm,exec,nochain TB logs into executed RV32 instruction streams.
QEMU TB instruction listings are keyed by guest PC; Trace lines record TB executions.
"""
import re,sys,csv,collections,pathlib
src=pathlib.Path(sys.argv[1]);dest=pathlib.Path(sys.argv[2])
blocks={};current=None;trace=[]
for line in src.open(errors="replace"):
 m=re.match(r'^IN:\s*$',line)
 if m:current=[];continue
 if current is not None:
  x=re.match(r'^0x([0-9a-fA-F]+):\s+([a-zA-Z][\w.]*)\s*(.*)',line)
  if x:current.append((int(x[1],16),x[2],x[3].split('#')[0].strip()));continue
  if not line.strip():
   if current:blocks[current[0][0]]=current
   current=None
 t=re.search(r'Trace\s+\d+:\s+0x[0-9a-fA-F]+\s+\[[^]]+/0x([0-9a-fA-F]+)',line)
 if t:trace.append(int(t[1],16))
if current:blocks[current[0][0]]=current
missing=sum(pc not in blocks for pc in trace)
with dest.open("w",newline="") as f:
 w=csv.writer(f);w.writerow(["seq","pc","op","args","tb_start"])
 seq=0
 for pc in trace:
  for addr,op,args in blocks.get(pc,[]):
   w.writerow([seq,hex(addr),op,args,hex(pc)]);seq+=1
print(f"{src.name}: TBs={len(trace)}, instructions={seq}, missing_TBs={missing}")
if missing or not trace or not seq:
 print('DEBUG: initial QEMU log lines:')
 print('\\n'.join(src.read_text(errors='replace').splitlines()[:75]))
 sys.exit(2)
