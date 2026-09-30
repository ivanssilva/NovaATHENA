#!/usr/bin/env python3
"""Static instruction and within-basic-block RAW graph proxy. NOT dynamic Tomasulo/ROB traces."""
import re,glob,csv,collections,os
os.makedirs("benchmark-results",exist_ok=True)
rows=[]
for file in sorted(glob.glob("benchmark-results/*.dis")):
 text=open(file).read().splitlines()
 instructions=[]
 for line in text:
  m=re.match(r'^\s*[0-9a-f]+:\s+(?:[0-9a-f]{2,8}\s+)+([a-z][\w.]*)\s*(.*)$',line)
  if m:instructions.append((m[1],m[2].split('#')[0].strip()))
 edges=collections.Counter();convergent=0;divergent=0;chain3=0;bb=[];blocks=[]
 for op,args in instructions:
  if op.startswith(('b','j')) or op in ('ret','jal','jalr'):
   if bb:blocks.append(bb);bb=[]
  else:bb.append((op,args))
 if bb:blocks.append(bb)
 for block in blocks:
  last={};indeg=collections.Counter();outdeg=collections.Counter();depth={}
  for i,(op,args) in enumerate(block):
   operands=[x.strip() for x in args.split(',')]
   # RISC-V GNU objdump uses destination-first syntax for these register-register instructions.
   rr=op in ('add','sub','and','or','xor','sll','srl','sra','slt','sltu','mul','mulh','mulhu','mulhsu')
   ri=op in ('addi','andi','ori','xori','slli','srli','srai','slti','sltiu')
   if not (rr or ri) or len(operands)<3:continue
   dest=operands[0];sources=operands[1:3] if rr else operands[1:2]
   producers=set(last[s] for s in sources if s in last and s!='zero')
   indeg[i]=len(producers);depth[i]=1+max((depth.get(p,1) for p in producers),default=0)
   for p in producers:outdeg[p]+=1;edges['RAW']+=1
   last[dest]=i
  convergent+=sum(v>=2 for v in indeg.values())
  divergent+=sum(v>=2 for v in outdeg.values())
  chain3+=sum(v>=3 for v in depth.values())
 c=collections.Counter(op for op,_ in instructions)
 rows.append(dict(kernel=os.path.basename(file).replace('.dis',''),instructions=len(instructions),basic_blocks=len(blocks),alu_ops=sum(c[k] for k in c if k in ('add','sub','and','or','xor','sll','srl','sra','slt','sltu','mul','addi','andi','ori','xori','slli','srli','srai','slti','sltiu')),static_raw_edges=edges['RAW'],static_convergence=convergent,static_divergence=divergent,static_chain_depth_ge3=chain3))
with open('benchmark-results/static_graph.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print("Analyzed",len(rows),"kernels; STATIC BASIC BLOCK PROXY ONLY")
