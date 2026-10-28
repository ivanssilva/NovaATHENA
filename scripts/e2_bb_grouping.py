#!/usr/bin/env python3
"""E2 closed: retrospective fixed-length groups of 1,2,4,8 dynamic basic blocks.
Only cross-BB RAW opportunity; NOT superblock validity, mapping or speedup.
"""
import csv,glob,os,json,hashlib,collections
from pathlib import Path
BR={'beq','bne','blt','bge','bltu','bgeu','jal','jalr','j','jr','ret','call','tail','c.j','c.jal','c.jr','c.jalr','c.beqz','c.bnez','ecall','ebreak','mret','sret'}
RR={'add','sub','and','or','xor','sll','srl','sra','slt','sltu','mul','mulh','mulhu','mulhsu'}
RI={'addi','andi','ori','xori','slli','srli','srai','slti','sltiu'}
ALIASES=dict(zip(['zero','ra','sp','gp','tp','t0','t1','t2','s0','s1','a0','a1','a2','a3','a4','a5','a6','a7','s2','s3','s4','s5','s6','s7','s8','s9','s10','s11','t3','t4','t5','t6'],['x'+str(i) for i in range(32)]))
ALIASES['fp']='x8'
def norm(x):return ALIASES.get(x.strip(),x.strip())
def operands(r):
 op=r['op'].lower().strip();a=[norm(x) for x in r['args'].split(',')]
 if op in RR and len(a)>=3:return a[0],a[1:3]
 if op in RI and len(a)>=2:return a[0],a[1:2]
 return None
def eval_group(bb):
 last={};edges=0;cross=0;depths={};maxdepth=0;eligible=0
 for bidx,block in enumerate(bb):
  for r in block:
   z=operands(r)
   if z is None:continue
   eligible+=1;dst,src=z;deps=[last[s] for s in src if s!='x0' and s in last]
   edges+=len(deps);cross+=sum(origin!=bidx for _,origin in deps)
   depth=1+max((d for d,_ in deps),default=0);maxdepth=max(maxdepth,depth)
   if dst!='x0':last[dst]=(depth,bidx)
 return eligible,edges,cross,maxdepth
paths=sorted(set(glob.glob('structural/*_O*.trace.csv')+glob.glob('structural/**/*.trace.csv',recursive=True)))
assert len(paths)==38,len(paths)
Path('e2-results').mkdir(exist_ok=True)
out=[];audits=[];totals=collections.Counter()
for path in paths:
 name=Path(path).name.removesuffix('.trace.csv');bench,opt=name.rsplit('_',1)
 stats={k:collections.Counter() for k in (1,2,4,8)}
 # Fixed nonoverlapping windows, anchored to the start of each trace.
 windows={k:[] for k in (1,2,4,8)}
 block=[];prev=None;nrows=0;nblocks=0
 def add_block():
  global nblocks
  if not block:return
  nblocks+=1
  for k in (1,2,4,8):
   w=windows[k];w.append(block[:])
   if len(w)==k:
    eligible,edges,cross,depth=eval_group(w)
    s=stats[k];s['regions']+=1;s['blocks']+=len(w);s['eligible']+=eligible;s['raw_edges']+=edges;s['cross_bb_raw_edges']+=cross;s['sum_depth']+=depth;s['max_depth']=max(s['max_depth'],depth)
    w.clear()
 with open(path,newline='') as f:
  reader=csv.DictReader(f);assert {'pc','op','args'}.issubset(reader.fieldnames)
  for r in reader:
   nrows+=1;pc=int(r['pc'],0)
   if prev is not None and (prev['op'].lower().strip() in BR or pc!=int(prev['pc'],0)+4):
    add_block();block=[]
   block.append(r);prev=r
 add_block()
 for k in (1,2,4,8):
  w=windows[k]
  if w:
   eligible,edges,cross,depth=eval_group(w)
   s=stats[k];s['regions']+=1;s['blocks']+=len(w);s['eligible']+=eligible;s['raw_edges']+=edges;s['cross_bb_raw_edges']+=cross;s['sum_depth']+=depth;s['max_depth']=max(s['max_depth'],depth)
  s=stats[k]
  assert s['blocks']==nblocks,(name,k,s['blocks'],nblocks)
  out.append(dict(benchmark=bench,opt=opt,group_BBs=k,dynamic_instructions=nrows,dynamic_BBs=nblocks,regions=s['regions'],eligible_alu_ops=s['eligible'],raw_edges=s['raw_edges'],cross_bb_raw_edges=s['cross_bb_raw_edges'],mean_region_depth=round(s['sum_depth']/s['regions'],7),max_region_depth=s['max_depth']))
  totals[(opt,k)]+=s['cross_bb_raw_edges']
 audits.append(dict(trace=name,sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest(),instructions=nrows,blocks=nblocks))
 print('E2_TRACE',name,'instructions',nrows,'BBs',nblocks,'cross_RAW_k8',stats[8]['cross_bb_raw_edges'],flush=True)
with open('e2-results/e2_per_trace.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
with open('e2-results/e2_aggregate.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['opt','group_BBs','cross_bb_raw_edges','regions','eligible_alu_ops','raw_edges'])
 for opt in ('O2','O3'):
  for k in (1,2,4,8):
   rows=[r for r in out if r['opt']==opt and r['group_BBs']==k]
   w.writerow([opt,k,sum(r['cross_bb_raw_edges'] for r in rows),sum(r['regions'] for r in rows),sum(r['eligible_alu_ops'] for r in rows),sum(r['raw_edges'] for r in rows)])
assert len(out)==152 and len(audits)==38
assert all(r['cross_bb_raw_edges']==0 for r in out if r['group_BBs']==1)
assert all(r['eligible_alu_ops']==next(q['eligible_alu_ops'] for q in out if q['benchmark']==r['benchmark'] and q['opt']==r['opt'] and q['group_BBs']==1) for r in out)
manifest=dict(experiment='E2-closed-retrospective-BB-groups',source_run=36850448602,source_artifact='athena-embench-structural',group_sizes=[1,2,4,8],semantics='nonoverlapping fixed-count dynamic BB groups, per trace, retrospective only',exclusions=['no branch prediction','no superblock formation','no CGRA mapping','no memory or control timing','no speedup claim','no static CFG'],traces=audits)
Path('e2-results/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
Path('e2-results/README.md').write_text('# E2 closed\n\nRetrospective dynamic groups of 1, 2, 4, 8 BBs. Counts ALU register-name RAW dependencies crossing BB boundaries and register-name dependency depth; neither a superblock implementation nor a performance estimate. Groups are nonoverlapping and trace-anchored. E1 block splitting reused. Results are not CGRA-mappability evidence.\n')
print('E2_AUDIT_PASS traces 38 rows 152',flush=True)
