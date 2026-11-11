#!/usr/bin/env python3
"""E7.1: full-writer RAW oracle vs independent synthetic rename observer.
Uses committed architectural traces; no measured OoO rename/dispatch events.
"""
import csv, glob, json, hashlib, collections
from pathlib import Path
A=dict(zip(('zero ra sp gp tp t0 t1 t2 s0 s1 a0 a1 a2 a3 a4 a5 a6 a7 s2 s3 s4 s5 s6 s7 s8 s9 s10 s11 t3 t4 t5 t6').split(),['x'+str(i) for i in range(32)]))
A['fp']='x8'
def n(s):return A.get(s.strip(),s.strip())
RR=set('add sub and or xor sll srl sra slt sltu mul mulh mulhu mulhsu div divu rem remu'.split())
RI=set('addi andi ori xori slli srli srai slti sltiu'.split())
LOAD=set('lb lh lw lbu lhu'.split())
STORE=set('sb sh sw'.split())
BR=set('beq bne blt bge bltu bgeu'.split())
J=set('jal jalr'.split())
UP=set('lui auipc'.split())
NO=set('ecall ebreak fence fence.i nop'.split())
def decode(op,args):
 a=[n(x) for x in args.split(',') if x.strip()]
 if op in RR and len(a)==3:return a[0],a[1:3],True
 if op in RI and len(a)==3:return a[0],[a[1]],True
 if op in LOAD and len(a)>=2:
  base=a[1].split('(')[-1].rstrip(')');return a[0],[base],False
 if op in STORE and len(a)>=2:
  base=a[1].split('(')[-1].rstrip(')');return None,[a[0],base],False
 if op in BR and len(a)>=2:return None,a[:2],False
 if op=='jal':
  if len(a)==1:return 'x1',[],False
  if len(a)>=2:return a[0],[],False
 if op=='jalr':
  if len(a)==1:return 'x1',[a[0].split('(')[-1].rstrip(')')],False
  if len(a)>=2:return a[0],[a[1].split('(')[-1].rstrip(')')],False
 if op in UP and len(a)>=2:return a[0],[],False
 if op in {'csrrw','csrrs','csrrc'} and len(a)==3:return a[0],[a[2]],False
 if op in {'csrrwi','csrrsi','csrrci'} and len(a)==3:return a[0],[],False
 if op in NO:return None,[],False
 # Conservative: unknown instruction is not silently ignored.
 raise ValueError('Unsupported opcode or operands: '+op+' '+args)
def edges_reference(decoded):
 last={}; out=[]
 for i,(dst,src,_) in enumerate(decoded):
  out.extend((i,j,last[s],s) for j,s in enumerate(src) if s!='x0' and s in last)
  if dst and dst!='x0':last[dst]=i
 return out
def edges_renamed(decoded):
 rat={}; out=[]
 for i,(dst,src,_) in enumerate(decoded):
  for j,s in enumerate(src):
   if s!='x0' and s in rat:out.append((i,j,rat[s][1],s))
  if dst and dst!='x0':rat[dst]=(1000+i,i)
 return out
def microcases():
 cases=[
 [('addi','x5,x0,1'),('lw','x5,0(x6)'),('add','x7,x5,x8')],
 [('add','x5,x1,x2'),('add','x5,x3,x4'),('sub','x6,x5,x7')],
 [('add','x5,x1,x2'),('sw','x5,0(x6)'),('add','x7,x5,x8')],
 [('add','x5,x1,x2'),('beq','x5,x0,8'),('add','x6,x5,x7')],
 [('lui','x5,42'),('add','x6,x5,x7'),('addi','x5,x0,2'),('add','x8,x5,x6')]
 ]
 for c in cases:
  d=[decode(op,args) for op,args in c]
  assert edges_reference(d)==edges_renamed(d),(c,edges_reference(d),edges_renamed(d))
microcases()
paths=sorted(set(glob.glob('structural/*_O*.trace.csv')+glob.glob('structural/**/*.trace.csv',recursive=True)))
assert len(paths)==38,('expected 38 traces',len(paths))
Path('e7-1-results').mkdir(exist_ok=True)
out=[]; unsupported=collections.Counter()
for path in paths:
 name=Path(path).name.removesuffix('.trace.csv')
 # streaming keeps memory bounded, tracks writer of ALL supported instructions
 oracle={};rat={};ref_count=obs_count=eligible=noneligible=0;rows=0;cross=0;prev_pc=None;prev_op=None;bb=0
 with open(path,newline='') as f:
  rd=csv.DictReader(f)
  assert {'pc','op','args'}.issubset(rd.fieldnames)
  for r in rd:
   op=r['op'].lower().strip();args=r['args'];pc=int(r['pc'],0)
   if prev_pc is not None and (prev_op in BR|J or pc!=prev_pc+4):bb+=1
   try: dst,src,is_eligible=decode(op,args)
   except ValueError:
    unsupported[op]+=1
    # Cannot safely proceed past an unknown writer.
    raise
   eligible+=int(is_eligible);noneligible+=int(not is_eligible)
   for j,s in enumerate(src):
    if s=='x0':continue
    a=oracle.get(s);b=rat.get(s)
    assert a==b,(name,rows,op,s,a,b)
    if a is not None:
     ref_count+=1;obs_count+=1
     cross+=int(a[1]!=bb)
   if dst and dst!='x0':
    oracle[dst]=(rows,bb)
    rat[dst]=(rows,bb)
   rows+=1;prev_pc=pc;prev_op=op
 out.append(dict(trace=name,rows=rows,eligible=eligible,noneligible=noneligible,raw_reference=ref_count,raw_rename=obs_count,cross_bb_raw=cross,sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest()))
 print('E7_1_TRACE',name,'rows',rows,'raw',ref_count,'cross_bb',cross,flush=True)
with open('e7-1-results/per_trace.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
summary=dict(experiment='E7.1',traces=len(out),instructions=sum(r['rows'] for r in out),raw_reference=sum(r['raw_reference'] for r in out),raw_observer=sum(r['raw_rename'] for r in out),cross_bb_raw=sum(r['cross_bb_raw'] for r in out),microcases=5,unsupported=dict(unsupported),observer='synthetic sequential rename-table oracle, not observed OoO dispatch',source_run=36850448602,source_artifact='athena-embench-structural',limitations=['No measured ROB, squash, rename timing or speculative instructions','Cross-BB counts include all supported register writers and readers; not mappability','Oracle and observer share decoding; equivalence is a consistency check, not independent proof of decoding correctness'])
assert summary['raw_reference']==summary['raw_observer']
Path('e7-1-results/manifest.json').write_text(json.dumps(summary,indent=2)+'\n')
print('E7_1_AUDIT_PASS traces',len(out),'instructions',summary['instructions'],flush=True)
